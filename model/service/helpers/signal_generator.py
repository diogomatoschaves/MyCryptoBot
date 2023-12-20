import logging
import os

import django

from model.backtesting.combining import StrategyCombiner
from model.service.external_requests import execute_order
from shared.utils.config_parser import get_config
from shared.utils.exceptions import StrategyInvalid
from shared.utils.helpers import convert_signal_to_text
from shared.utils.logger import configure_logger
from shared.data.queries import get_data
from model.strategies.trend import Momentum
from model.strategies.moving_average import MovingAverageConvergenceDivergence, MovingAverageCrossover, MovingAverage
from model.strategies.mean_reversion import BollingerBands

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import StructuredData

config_vars = get_config('model')

configure_logger(os.getenv("LOGGER_LEVEL", config_vars.logger_level))


def strategy_combiner(strategies, data):

    strategies_objs = []

    for strategy in strategies:
        try:
            strategy_obj = eval(strategy["name"])(**strategy["params"])
        except NameError:
            raise StrategyInvalid(strategy["name"])

        strategies_objs.append(strategy_obj)

    combined_strategy = StrategyCombiner(strategies_objs, data=data)

    return combined_strategy


def send_signal(
    pipeline,
    bearer_token,
    header=''
):
    data = get_data(StructuredData, None, pipeline["symbol"], pipeline["interval"], pipeline["exchange"])

    if len(data) == 0:
        logging.debug(header + f"Empty DataFrame, aborting.")
        return False

    combined_strategy = strategy_combiner(pipeline["strategies"], data)

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
