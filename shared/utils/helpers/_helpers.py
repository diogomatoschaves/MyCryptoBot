import json
import os
from collections import namedtuple
from datetime import datetime

import django
import pandas as pd
import pytz
from stratestic.backtesting.helpers import Trade

from shared.exchanges.binance import constants as const
from shared.utils.exceptions import NoSuchPipeline

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline, Trade as DBTrade

escapes = ''.join([chr(char) for char in range(1, 32)])
translator = str.maketrans('', '', escapes)


LOADING = "Loading"


PIPELINE = namedtuple(
    'Pipeline',
    [
        "id",
        "symbol",
        "strategy",
        "strategy_combination",
        "candle_size",
        "exchange",
        "paper_trading",
        "active",
        "initial_equity",
        "current_equity",
        "leverage"
    ]
)


def get_root_dir():
    return os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            '../../..'
        )
    )


def get_logging_row_header(cache, pipeline):
    header = f"{pipeline.symbol.name}|{pipeline.name}|{pipeline.id}|{pipeline.interval}: "

    cache.set(
        f"pipeline {pipeline.id}",
        json.dumps(header)
    )

    return header


def get_item_from_cache(cache, key):

    item = cache.get(f"pipeline {key}")

    return item if item else '""'


def add_pipeline_loading(cache, pipeline_id):

    loading = set(json.loads(cache.get(LOADING))) if cache.get(LOADING) is not None else set()

    loading.add(pipeline_id)

    cache.set(
        LOADING,
        json.dumps(list(set(loading)))
    )


def remove_pipeline_loading(cache, pipeline_id):

    loading = set(json.loads(cache.get(LOADING))) if cache.get(LOADING) is not None else set()

    try:
        loading.remove(pipeline_id)
    except KeyError:
        pass

    cache.set(
        LOADING,
        json.dumps(list(loading))
    )


def is_pipeline_loading(cache, pipeline_id):

    loading = set(json.loads(cache.get(LOADING)))

    return pipeline_id in loading


def get_pipeline_data(pipeline_id, return_obj=False, ignore_exception=False):

    if pipeline_id is None and ignore_exception:
        return None

    try:
        pipeline = Pipeline.objects.get(id=pipeline_id)
    except Pipeline.DoesNotExist:
        if ignore_exception:
            return None
        else:
            raise NoSuchPipeline(pipeline_id)

    if return_obj:
        return pipeline
    else:
        pipeline = PIPELINE(
            id=pipeline_id,
            symbol=pipeline.symbol.name,
            strategy=[obj.as_json() for obj in pipeline.strategy.all()],
            strategy_combination=pipeline.strategy_combination,
            candle_size=pipeline.interval,
            exchange=pipeline.exchange.name,
            paper_trading=pipeline.paper_trading,
            active=pipeline.active,
            initial_equity=pipeline.initial_equity,
            current_equity=pipeline.current_equity,
            leverage=pipeline.leverage
        )

        return pipeline


def get_input_dimensions(lst, n_dim=0):
    """
    Recursively determines the dimensions of a nested list or tuple.

    Parameters:
    -----------
    lst : list or tuple
        The nested list or tuple to determine the dimensions of.
    n_dim : int, optional
        Internal parameter to track the current nesting level (default is 0).

    Returns:
    --------
    int
        The number of dimensions in the nested structure. For a flat list, the
        result is 1. For each level of nesting, the result increases by 1.

    Examples:
    ---------
    >>> get_input_dimensions([1, 2, 3])
    1

    >>> get_input_dimensions([[1, 2], [3, 4]])
    2

    >>> get_input_dimensions([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    3
    """
    if isinstance(lst, (list, tuple)):
        return get_input_dimensions(lst[0], n_dim + 1) if len(lst) > 0 else 0
    else:
        return n_dim


def convert_trade(trade: DBTrade):
    """
    Converts a database Trade object into a standardized Trade object with structured attributes.

    Parameters
    ----------
    trade : Trade object or similar
        The raw trade object containing trade details such as open and close times, prices,
         amount, side, and profit.

    Returns
    -------
    Trade
        A structured Trade object containing the processed information from the db trade.

    """

    return Trade(
        entry_date=trade.open_time,
        exit_date=trade.close_time,
        entry_price=trade.open_price,
        exit_price=trade.close_price,
        units=trade.amount,
        side=trade.side,
        profit=trade.pnl,
        pnl=trade.pnl_pct
    )


def get_minimum_lookback_date(max_window, candle_size):
    """
    Calculates the minimum lookback date required based on the maximum window size and the candle size.

    Parameters
    ----------
    max_window : int
        The maximum window size used in strategy calculations, which determines how far back the data
         needs to go.
    candle_size : str
        The size of the candle (e.g., "1h", "1d") which impacts the calculation of the lookback period.

    Returns
    -------
    datetime
        The calculated minimum lookback date as a datetime object, timezone-aware and adjusted to UTC.

    Notes
    -----
    The function uses a multiplier (1.4) to ensure a slightly larger buffer is included in the
     lookback period.
    """
    return (datetime.now().astimezone(pytz.utc) -
            pd.Timedelta(const.CANDLE_SIZES_MAPPER[candle_size]) * max_window * 1.4)


def get_pipeline_max_window(pipeline_id, default_min_rows):
    """
    Determines the maximum window size for a given pipeline by inspecting its strategies and parameters.

    Parameters
    ----------
    pipeline_id : int
        The identifier of the pipeline.
    default_min_rows : int
        The default minimum number of rows to fall back on if no specific value is determined.

    Returns
    -------
    int
        The maximum window size calculated based on the strategy parameters
        within the pipeline, or the default minimum if no specific value is determined.

    Raises
    ------
    Pipeline.DoesNotExist
        If no pipeline with the given `pipeline_id` exists.

    Notes
    -----
    This function is useful for dynamically adjusting the amount of data fetched
    based on the needs of the pipeline's strategies.
    """
    try:
        pipeline = Pipeline.objects.get(id=pipeline_id).as_json()
    except Pipeline.DoesNotExist:
        return int(default_min_rows)

    strategies = pipeline["strategy"]

    max_value_params = 0
    for strategy in strategies:

        try:
            max_value = max([
                value for param, value in strategy["params"].items()
                if isinstance(value, (int, float))
            ])

            if max_value > max_value_params:
                max_value_params = max_value
        except ValueError:
            continue

    return max(max_value_params, int(default_min_rows))
