import logging
import os

import django
from flask import jsonify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Exchange
import shared.exchanges.binance.constants as const

APP_NAME = os.getenv("APP_NAME")

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
            return jsonify({"response": "A symbol must be included in the request."})

        try:
            Symbol.objects.get(name=symbol)
        except Symbol.DoesNotExist as e:
            logging.debug(symbol)
            logging.debug(e)
            return jsonify({"response": f"{symbol} is not a valid symbol."})

    if "exchange" in kwargs:
        exchange = kwargs["exchange"]

        if exchange is None:
            return jsonify({"response": "An exchange must be included in the request."})

        try:
            Exchange.objects.get(name=exchange.lower())
        except (Exchange.DoesNotExist, AttributeError) as e:
            logging.debug(exchange)
            logging.debug(e)
            return jsonify({"response": f"{exchange} is not a valid exchange."})

    if "candle_size" in kwargs:
        candle_size = kwargs["candle_size"]
        if candle_size not in const.CANDLE_SIZES_MAPPER:
            logging.debug(candle_size)
            return jsonify({"response": f"{candle_size} is not a valid candle size."})

    if "strategy" in kwargs:
        strategy = kwargs["strategy"]

        if strategy is None:
            return jsonify({"response": "A strategy must be included in the request."})

        if strategy in STRATEGIES:
            if "params" in kwargs:
                params = kwargs["params"]
                for key in params:
                    if key not in STRATEGIES[strategy]["params"]:
                        logging.debug(key)
                        return jsonify({"response": f"Provided {key} in params is not valid."})
        else:
            logging.debug(strategy)
            return jsonify({"response": f"{strategy} is not a valid strategy."})

    return None
