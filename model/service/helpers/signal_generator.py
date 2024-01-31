import logging
import os

import django
from stratestic.backtesting.combining import StrategyCombiner
from stratestic.strategies.trend import Momentum
from stratestic.strategies.moving_average import MovingAverageConvergenceDivergence, MovingAverageCrossover, MovingAverage
from stratestic.strategies.mean_reversion import BollingerBands

from model.strategies import *
from model.service.external_requests import execute_order
from model.service.helpers import convert_signal_to_text
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


def strategy_combiner(strategies, combination_method, data):

    strategies_objs = []

    for strategy in strategies:
        try:
            strategy_obj = eval(strategy["name"])(**strategy["params"])
        except NameError:
            raise StrategyInvalid(strategy["name"])

        strategies_objs.append(strategy_obj)

    combined_strategy = StrategyCombiner(strategies_objs, method=combination_method, data=data)

    return combined_strategy


def send_signal(
    pipeline,
    bearer_token,
    header=''
):
    max_window = get_pipeline_max_window(pipeline["id"])

    start_date = get_minimum_lookback_date(max_window, pipeline["interval"])

    data = get_data(StructuredData, start_date, pipeline["symbol"], pipeline["interval"], pipeline["exchange"])

    if len(data) == 0:
        logging.debug(header + f"Empty DataFrame, aborting.")
        return False

    combined_strategy = strategy_combiner(pipeline["strategies"], pipeline["strategy_combination"], data)

    logging.info(header + "Generating signal.")

    signal = combined_strategy.get_signal()

    logging.debug(header + f"{convert_signal_to_text(signal)} signal generated.")

    return trigger_order(pipeline["id"], signal, bearer_token, header=header)


def trigger_order(pipeline_id, signal, bearer_token, header=''):

    response = execute_order(pipeline_id, signal, bearer_token, header=header)

    if response is None:
        return False

    if "success" in response and response["success"]:
        logging.debug(header + "Order was executed successfully.")
        return True
    else:
        logging.warning(response)
        return False
