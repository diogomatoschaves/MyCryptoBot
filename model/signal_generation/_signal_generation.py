import logging
import os
from typing import Literal

import django
import pandas as pd
from stratestic.backtesting.combining import StrategyCombiner
from stratestic.strategies import *

from model.strategies import *
from model.service.helpers import LOCAL_MODELS_LOCATION
from model.service.cloud_storage import upload_models
from model.service.external_requests import execute_order
from model.signal_generation._helpers import convert_signal_to_text, strategies_defaults
from shared.utils.config_parser import get_config
from shared.utils.exceptions import StrategyInvalid
from shared.utils.helpers import get_pipeline_max_window, get_minimum_lookback_date
from shared.utils.logger import configure_logger
from shared.data.queries import get_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import StructuredData

config_vars = get_config('model')

configure_logger(os.getenv("LOGGER_LEVEL", config_vars.logger_level))


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
        try:
            extra_args = strategies_defaults.get(strategy["name"], {})

            strategy_obj = eval(strategy["name"])(**strategy["params"], **extra_args)
        except NameError:
            raise StrategyInvalid(strategy["name"])

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
    max_window = get_pipeline_max_window(pipeline["id"], config_vars.default_min_rows)

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

    return trigger_order(pipeline["id"], signal, bearer_token, header=header)


def trigger_order(pipeline_id, signal, bearer_token, header=''):
    """
    Executes a trading order based on a generated signal and the specified pipeline configuration.

    Parameters
    ----------
    pipeline_id : int
        The identifier of the trading pipeline configuration.
    signal : int
        The trading signal generated by the composite strategy, indicating whether to buy, sell, or hold.
    bearer_token : str
        The authentication token required for executing orders through the external trading service.
    header : str, optional
        Additional information or prefix for logging purposes, default is an empty string.

    Returns
    -------
    bool
        True if the order execution response is successful, False otherwise.

    Notes
    -----
    - The function communicates with an external trading service to execute the order.
        The success of the order execution is determined by the response from this service.
    - Logging provides feedback on the execution process and the outcome.
    """

    response = execute_order(pipeline_id, signal, bearer_token, header=header)

    if response is None:
        return False

    if "success" in response and response["success"]:
        logging.debug(header + "Order was executed successfully.")
        return True
    else:
        logging.warning(response)
        return False
