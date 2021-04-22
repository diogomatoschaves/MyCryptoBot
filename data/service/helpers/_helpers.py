import logging
import os

import django
from flask import jsonify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from data.service.helpers.responses import RESPONSES
from database.model.models import Symbol, Exchange
import shared.exchanges.binance.constants as const

MODEL_APP_ENDPOINTS = {
    "GENERATE_SIGNAL": lambda host_url: f"{host_url}/generate_signal",
    "CHECK_JOB": lambda host_url, job_id: f"{host_url}/check_job/{job_id}"
}

EXECUTION_APP_ENDPOINTS = {
    "START_SYMBOL_TRADING": lambda host_url: f"{host_url}/start_symbol_trading",
    "STOP_SYMBOL_TRADING": lambda host_url: f"{host_url}/stop_symbol_trading",
}

STRATEGIES = {
    'BollingerBands': {
        "params": {"ma", "sd"}
    },
    'MachineLearning': {
        "params": {
            "estimator",
            "lag_features",
            "rolling_features",
            "excluded_features",
            "nr_lags",
            "windows",
            "test_size",
            "degree",
            "print_results"
        }
    },
    'Momentum': {
        "params": {"window"}
    },
    'MovingAverageConvergenceDivergence': {
        "params": {"window_slow", "window_fast", "window_signal"}
    },
    'MovingAverage': {
        "params": {"sma", "moving_av"}
    },
    'MovingAverageCrossover': {
        "params": {"SMA_S", "SMA_L", "moving_av"}
    },
}


def check_input(**kwargs):

    if "symbol" in kwargs:
        symbol = kwargs["symbol"]

        if symbol is None:
            return jsonify(RESPONSES["SYMBOL_REQUIRED"])

        try:
            Symbol.objects.get(name=symbol)
        except Symbol.DoesNotExist as e:
            logging.debug(symbol)
            logging.debug(e)
            return jsonify(RESPONSES["SYMBOL_INVALID"](symbol))

    if "exchange" in kwargs:
        exchange = kwargs["exchange"]

        if exchange is None:
            return jsonify(RESPONSES["EXCHANGE_REQUIRED"])

        try:
            Exchange.objects.get(name=exchange.lower())
        except (Exchange.DoesNotExist, AttributeError) as e:
            logging.debug(exchange)
            logging.debug(e)
            return jsonify(RESPONSES["EXCHANGE_INVALID"](exchange))

    if "candle_size" in kwargs:
        candle_size = kwargs["candle_size"]

        if candle_size is None:
            return jsonify(RESPONSES["CANDLE_SIZE_REQUIRED"])

        if candle_size not in const.CANDLE_SIZES_MAPPER:
            logging.debug(candle_size)
            return jsonify(RESPONSES["CANDLE_SIZE_INVALID"](candle_size))

    if "strategy" in kwargs:
        strategy = kwargs["strategy"]

        if strategy is None:
            return jsonify(RESPONSES["STRATEGY_REQUIRED"])

        if strategy in STRATEGIES:
            if "params" in kwargs:
                params = kwargs["params"]
                for key in params:
                    if key not in STRATEGIES[strategy]["params"]:
                        logging.debug(key)
                        return jsonify(RESPONSES["STRATEGY_INVALID"](key))
        else:
            logging.debug(strategy)
            return jsonify(RESPONSES["STRATEGY_INVALID"](strategy))

    return None
