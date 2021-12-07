import json
import logging
import os

import django
import redis

from model.service.external_requests import execute_order
from shared.utils.helpers import convert_signal_to_text, get_item_from_cache
from shared.utils.logger import configure_logger
from shared.data.queries import get_data
from model.strategies.trend import Momentum
from model.strategies.moving_average import MovingAverageConvergenceDivergence, MovingAverageCrossover, MovingAverage
from model.strategies.mean_reversion import BollingerBands
from model.strategies.machine_learning import MachineLearning

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import StructuredData

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


def get_signal(pipeline_id, symbol, candle_size, exchange, strategy, params=None):

    if params is None:
        params = {}

    data = get_data(StructuredData, None, symbol, candle_size, exchange)

    if len(data) == 0:
        logging.debug(f"Empty DataFrame. {symbol}, {candle_size}, {exchange}")
        return False

    # TODO: Compact all this with eval
    if strategy == 'MovingAverageConvergenceDivergence':
        signal_gen = MovingAverageConvergenceDivergence(**params, data=data)

    elif strategy == 'MovingAverage':
        signal_gen = MovingAverage(**params, data=data)

    elif strategy == 'MovingAverageCrossover':
        signal_gen = MovingAverageCrossover(**params, data=data)

    elif strategy == 'BollingerBands':
        signal_gen = BollingerBands(**params, data=data)

    elif strategy == 'Momentum':
        signal_gen = Momentum(**params, data=data)

    elif strategy == 'MachineLearning':
        # TODO: Check current error
        # TODO: Must resample data and delete entries
        #  that would not make sense according to number of lags
        signal_gen = MachineLearning(**params, data=data)

    else:
        logging.info(f"Invalid strategy: %s" % strategy)
        return False

    signal = signal_gen.get_signal()

    logging.debug(json.loads(get_item_from_cache(cache, pipeline_id)) +
                  f"{convert_signal_to_text(signal)} signal generated")

    return trigger_order(signal, symbol, exchange, pipeline_id)


def trigger_order(signal, symbol, exchange, pipeline_id):

    response = execute_order(symbol, signal, exchange)

    if "success" in response and response["success"]:
        logging.debug(json.loads(get_item_from_cache(cache, pipeline_id)) +
                      "Order was executed successfully.")
        return True
    else:
        logging.warning(response["response"])
        return False

