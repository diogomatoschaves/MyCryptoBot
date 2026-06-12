import logging
import os
import time
from datetime import datetime, timedelta
from typing import Literal

import django
import pandas as pd
import pytz
from requests import ConnectionError, ReadTimeout
from stratestic.backtesting.combining import StrategyCombiner
from stratestic.strategies import *
from stratestic.strategies._mixin import StrategyMixin

from model.strategies import *
from model.service.helpers import LOCAL_MODELS_LOCATION
from model.service.cloud_storage import upload_models
from model.service.external_requests import execute_order
from model.signal_generation._exceptions import OrderDeliveryError, StaleSignal
from model.signal_generation._helpers import convert_signal_to_text, strategies_defaults
import shared.exchanges.binance.constants as const
from shared.utils.notifier import send_alert
from shared.utils.settings import settings
from shared.utils.exceptions import StrategyInvalid
from shared.utils.helpers import get_pipeline_max_window, get_minimum_lookback_date
from shared.utils.logger import configure_logger
from shared.data.queries import get_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import StructuredData


configure_logger(settings.logger_level)

_strategy_registry = None


def get_strategy_class(name):
    """Resolve a strategy class by name from a whitelist of StrategyMixin
    subclasses already imported into this module. Replaces eval() of a
    DB-provided string, which was an arbitrary-code-execution path.
    """
    global _strategy_registry
    if _strategy_registry is None:
        _strategy_registry = {
            cls_name: obj for cls_name, obj in globals().items()
            if isinstance(obj, type) and issubclass(obj, StrategyMixin) and obj is not StrategyMixin
        }

    try:
        return _strategy_registry[name]
    except KeyError:
        raise StrategyInvalid(name)


def strategy_combiner(strategies, combination_method: Literal["Unanimous", "Majority"], data: pd.DataFrame):
    """
    Combines multiple trading strategies into a single composite strategy using a specified combination method.

    Parameters
    ----------
    strategies : list of dicts
        A list where each dict contains the 'name' of the trading strategy and its 'params'.
        These strategies are to be combined into a single composite strategy.
    combination_method : Literal["Unanimous", "Majority"]
        The method used to combine the individual strategies' signals into a single signal.
        Common methods include 'vote', 'average', or custom-defined methods.
    data : pd.DataFrame
        The market data that the composite strategy will be applied to. It should include the
        necessary columns as required by the individual strategies.

    Returns
    -------
    StrategyCombiner
        An instance of the StrategyCombiner class, representing the composite strategy
        ready to be used on the provided data.

    Raises
    ------
    StrategyInvalid
        If any of the strategy names provided in the `strategies` list do not correspond to a defined strategy.

    Examples
    --------
    >>> combined_strategy = strategy_combiner(
            strategies=[{"name": "MovingAverageCrossover", "params": {"sma_s": 5, "sma_l": 20}}],
            combination_method="Majority",
            data=data
        )
    """

    strategies_objs = []

    for strategy in strategies:
        extra_args = strategies_defaults.get(strategy["name"], {})

        strategy_cls = get_strategy_class(strategy["name"])
        strategy_obj = strategy_cls(**strategy["params"], **extra_args)

        strategies_objs.append(strategy_obj)

    return StrategyCombiner(strategies_objs, method=combination_method, data=data)


def signal_generator(pipeline, bearer_token, header=''):
    """
    Generates a trading signal based on a composite strategy and attempts to execute
    a trade based on this signal.

    Parameters
    ----------
    pipeline : dict
        A configuration dict for the trading pipeline, including 'id', 'strategies', 'strategy_combination',
         'interval', 'symbol', and 'exchange'.
    bearer_token : str
        The authentication token required for executing orders through the external trading service.
    header : str, optional
        Additional information or prefix for logging purposes, default is an empty string.

    Returns
    -------
    bool
        True if the order is successfully executed, False otherwise.

    Notes
    -----
    - This function first retrieves market data based on the specified pipeline configuration,
        then generates a signal using the combined strategy, and finally attempts to execute
        a trade based on this signal.
    - Logging is used to provide information about the process and any potential issues encountered.
    """
    deadline = compute_delivery_deadline(pipeline)

    max_window = get_pipeline_max_window(pipeline["id"], settings.default_min_rows)

    start_date = get_minimum_lookback_date(max_window, pipeline["interval"])

    data = get_data(StructuredData, start_date, pipeline["symbol"], pipeline["interval"], pipeline["exchange"])

    if len(data) == 0:
        logging.debug(header + f"Empty DataFrame, aborting.")
        return False

    combined_strategy = strategy_combiner(pipeline["strategies"], pipeline["strategy_combination"], data)

    # Upload new models to the cloud
    if os.getenv('USE_CLOUD_STORAGE'):
        upload_models(LOCAL_MODELS_LOCATION)

    logging.info(header + "Generating signal.")

    signal = combined_strategy.get_signal()

    logging.debug(header + f"{convert_signal_to_text(signal)} signal generated.")

    return trigger_order(pipeline["id"], signal, bearer_token, deadline=deadline, header=header)


# transport-level failure code produced by json_error_handler when the
# execution service returns garbage (bad gateway etc.)
TRANSPORT_ERROR_CODE = 502

# in-job delivery retry budget: stays inside the data service's 50s job
# polling window so the poller never gives up on a job that is still retrying
MAX_DELIVERY_SECONDS = 40

DELIVERY_BACKOFFS = [5, 10, 20]


def compute_delivery_deadline(pipeline):
    """
    Returns the moment after which delivering this signal is no longer safe.

    The deadline is the earlier of: the close of the candle the signal was
    computed for (a later order would race the next candle's signal), and a
    fixed in-job retry budget that keeps the job inside the data service's
    polling window.

    Raises
    ------
    StaleSignal
        If the candle period has already elapsed when the job starts (queue
        backlog / worker outage): the order must not fire at all.
    """
    now = datetime.now(tz=pytz.utc)
    job_deadline = now + timedelta(seconds=MAX_DELIVERY_SECONDS)

    enqueued_at = pipeline.get("enqueued_at")
    if not enqueued_at:
        # jobs enqueued by an older app version during a deploy window
        return job_deadline

    try:
        enqueued = datetime.fromisoformat(enqueued_at)
        candle_period = timedelta(**const.CANDLE_SIZE_TIMEDELTA[pipeline["interval"]])
    except (KeyError, TypeError, ValueError):
        return job_deadline

    candle_deadline = enqueued + candle_period

    if now >= candle_deadline:
        raise StaleSignal(pipeline.get("id"), enqueued_at)

    return min(candle_deadline, job_deadline)


def trigger_order(pipeline_id, signal, bearer_token, deadline=None, header=''):
    """
    Delivers a trading signal to the execution service, retrying transport
    failures with backoff until the delivery deadline.

    The execution endpoint is safe to retry: it compares the current position
    with the signal (no-op on match) and order placement itself is idempotent
    via client order ids. Business failures (the service received the signal
    and declined it) are returned immediately - retrying cannot change them.

    Returns
    -------
    bool
        True if the order was executed successfully, False if the execution
        service declined the signal.

    Raises
    ------
    OrderDeliveryError
        When the execution service stays unreachable past the deadline. The
        RQ job fails, keeping the loss visible (FailedJobRegistry + alert)
        instead of silently dropping the order.
    """
    attempt = 0

    while True:
        response = None

        try:
            response = execute_order(pipeline_id, signal, bearer_token, header=header)
        except (ConnectionError, ReadTimeout) as e:
            logging.warning(header + f"Could not reach the execution service: {e!r}")

        if response is not None:
            if response.get("success"):
                logging.debug(header + "Order was executed successfully.")
                return True

            if response.get("code") != TRANSPORT_ERROR_CODE:
                # delivered and declined: a structured business failure that
                # retrying with the same arguments cannot fix
                logging.warning(response)
                return False

            logging.warning(header + f"Transport error from the execution service: {response}")

        backoff = DELIVERY_BACKOFFS[min(attempt, len(DELIVERY_BACKOFFS) - 1)]

        if deadline is None or datetime.now(tz=pytz.utc) + timedelta(seconds=backoff) >= deadline:
            raise OrderDeliveryError(pipeline_id, signal)

        logging.info(header + f"Retrying order delivery in {backoff}s.")
        time.sleep(backoff)
        attempt += 1


def signal_failure_handler(job, connection, exc_type, exc_value, tb):
    """
    RQ failure callback: makes failed signal jobs loud. Runs on the worker
    when a job raises; the job itself stays inspectable in the
    FailedJobRegistry for the configured failure_ttl.
    """
    pipeline = job.args[0] if job.args else {}
    pipeline_id = pipeline.get("id") if isinstance(pipeline, dict) else None

    is_lost_order = isinstance(exc_value, OrderDeliveryError)

    send_alert(
        title="Signal job failed" if not is_lost_order else "Order NOT placed - delivery failed",
        body=(
            f"Pipeline {pipeline_id}: {exc_type.__name__}: {exc_value}. "
            f"The job is kept in the failed-job registry for inspection."
        ),
        severity="critical" if is_lost_order else "warning",
        dedup_key=f"signal-job-{pipeline_id}",
    )
