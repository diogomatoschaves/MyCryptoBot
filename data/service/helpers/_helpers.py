import json
import logging
import os

import django
from flask import jsonify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from data.service.helpers.responses import Responses
from database.model.models import Symbol, Exchange, Pipeline
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
        "name": "Bollinger Bands",
        "params": ["ma", "sd"]
    },
    'MachineLearning': {
        "name": "Machine Learning",
        "params": [
            "estimator",
            "lag_features",
            "rolling_features",
            "excluded_features",
            "nr_lags",
            "windows",
            "test_size",
            "degree",
            "print_results"
        ]
    },
    'Momentum': {
        "name": "Momentum",
        "params": ["window"]
    },
    'MovingAverageConvergenceDivergence': {
        "name": "Moving Average Convergence Divergence",
        "params": ["window_slow", "window_fast", "window_signal"]
    },
    'MovingAverage': {
        "name": "Moving Average",
        "params": ["sma", "moving_av"]
    },
    'MovingAverageCrossover': {
        "name": "Moving Average Crossover",
        "params": ["SMA_S", "SMA_L", "moving_av"]
    },
}


def check_input(**kwargs):

    if "symbol" in kwargs:
        symbol = kwargs["symbol"]

        if symbol is None:
            return jsonify(Responses.SYMBOL_REQUIRED)

        try:
            Symbol.objects.get(name=symbol)
        except Symbol.DoesNotExist as e:
            logging.debug(symbol)
            logging.debug(e)
            return jsonify(Responses.SYMBOL_INVALID(symbol))

    if "exchange" in kwargs:
        exchange = kwargs["exchange"]

        if exchange is None:
            return jsonify(Responses.EXCHANGE_REQUIRED)

        try:
            Exchange.objects.get(name=exchange.lower())
        except (Exchange.DoesNotExist, AttributeError) as e:
            logging.debug(exchange)
            logging.debug(e)
            return jsonify(Responses.EXCHANGE_INVALID(exchange))

    if "candle_size" in kwargs:
        candle_size = kwargs["candle_size"]

        if candle_size is None:
            return jsonify(Responses.CANDLE_SIZE_REQUIRED)

        if candle_size not in const.CANDLE_SIZES_MAPPER:
            logging.debug(candle_size)
            return jsonify(Responses.CANDLE_SIZE_INVALID(candle_size))

    if "strategy" in kwargs:
        strategy = kwargs["strategy"]

        if strategy is None:
            return jsonify(Responses.STRATEGY_REQUIRED)

        if strategy in STRATEGIES:
            if "params" in kwargs:
                params = kwargs["params"]
                for key in params:
                    if key not in STRATEGIES[strategy]["params"]:
                        logging.debug(key)
                        return jsonify(Responses.PARAMS_INVALID(key))
        else:
            logging.debug(strategy)
            return jsonify(Responses.STRATEGY_INVALID(strategy))

    return None


def get_or_create_pipeline(symbol, candle_size, strategy, exchange, params, paper_trading):

    columns = dict(
        symbol_id=symbol,
        interval=candle_size,
        strategy=strategy,
        exchange_id=exchange,
        params=json.dumps(params),
        paper_trading=paper_trading
    )

    try:
        pipeline = Pipeline.objects.get(**columns)

        if pipeline.active:
            return pipeline, jsonify(Responses.DATA_PIPELINE_ONGOING)
        else:
            pipeline.active = True

        pipeline.save()

    except Pipeline.DoesNotExist:
        pipeline = Pipeline.objects.create(**columns)

    return pipeline, None
