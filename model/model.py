import logging
import os

import django

from shared.utils.logger import configure_logger
from shared.data.queries import get_data
from model.strategies import (
    MovingAverageConvergenceDivergence,
    MovingAverage,
    MovingAverageCrossover,
    BollingerBands,
    Momentum,
    MachineLearning
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import StructuredData

configure_logger()


def gen_signal(symbol, candle_size, exchange, strategy, params):

    data = get_data(StructuredData, None, symbol, candle_size, exchange)

    if len(data) == 0:
        logging.debug(f"Empty DataFrame. {symbol}, {candle_size}, {exchange}")
        return

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
        # TODO: Must resample data and delete entries that would not make sense according to lags
        signal_gen = MachineLearning(**params, data=data)

    else:
        logging.info(f"Invalid strategy: %s" % strategy)
        return

    signal = signal_gen.get_signal()

    logging.info(f"Signal {signal} generated for symbol {symbol} and strategy: {strategy}")

    # TODO: Send signal to Order Execution service
