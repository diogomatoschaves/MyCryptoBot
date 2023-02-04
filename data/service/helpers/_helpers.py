import datetime
import json
import logging
import os

import django
import pytz

from data.service.helpers.exceptions import *
from data.service.helpers.exceptions.data_pipeline_ongoing import DataPipelineOngoing
from shared.utils.exceptions import SymbolInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Exchange, Pipeline, Symbol
import shared.exchanges.binance.constants as const

MODEL_APP_ENDPOINTS = {
    "GENERATE_SIGNAL": lambda host_url: f"{host_url}/generate_signal",
    "CHECK_JOB": lambda host_url, job_id: f"{host_url}/check_job/{job_id}",
    "GET_STRATEGIES": lambda host_url: f"{host_url}/strategies",
}

EXECUTION_APP_ENDPOINTS = {
    "START_SYMBOL_TRADING": lambda host_url: f"{host_url}/start_symbol_trading",
    "STOP_SYMBOL_TRADING": lambda host_url: f"{host_url}/stop_symbol_trading",
    "GET_PRICE": lambda host_url, symbol: f"{host_url}/prices?symbol={symbol}",
    "GET_BALANCE": lambda host_url: f"{host_url}/futures_account_balance",
    "GET_OPEN_POSITIONS": lambda host_url: f"{host_url}/open-positions",
}


def check_input(binance_client, strategies, **kwargs):

    if "pipeline_id" in kwargs and kwargs["pipeline_id"] and Pipeline.objects.filter(id=kwargs["pipeline_id"]).exists():
        return True

    if "symbol" in kwargs:
        symbol = kwargs["symbol"]

        if symbol is None:
            raise SymbolRequired

        if not Symbol.objects.filter(name=symbol).exists():
            raise SymbolInvalid(symbol)

    if "exchange" in kwargs:
        exchange = kwargs["exchange"]

        if exchange is None:
            raise ExchangeRequired

        try:
            Exchange.objects.get(name=exchange.lower())
        except (Exchange.DoesNotExist, AttributeError) as e:
            raise ExchangeInvalid(exchange)

    if "candle_size" in kwargs:
        candle_size = kwargs["candle_size"]

        if candle_size is None:
            raise CandleSizeRequired

        if candle_size not in const.CANDLE_SIZES_MAPPER:
            raise CandleSizeInvalid(candle_size)

    if "strategy" in kwargs:
        strategy = kwargs["strategy"]

        if strategy is None:
            raise StrategyRequired

        if strategy in strategies:
            if "params" in kwargs:
                params = kwargs["params"]

                invalid_params = []
                for key in params:
                    if key not in strategies[strategy]["params"] and key not in strategies[strategy]["optionalParams"]:
                        logging.debug(key)
                        invalid_params.append(key)

                if len(invalid_params) > 0:
                    raise ParamsInvalid(', '.join(invalid_params))

            required_params = []
            for param in strategies[strategy]["params"]:
                if param not in kwargs.get("params", {}):
                    required_params.append(param)

            if len(required_params) > 0:
                raise ParamsRequired(', '.join(required_params))
        else:
            raise StrategyInvalid(strategy)

    if "name" not in kwargs or kwargs["name"] is None:
        raise NameRequired
    else:
        name = kwargs["name"]
        if not isinstance(name, str) or Pipeline.objects.filter(name=name).exists():
            raise NameInvalid(name)

    if "color" not in kwargs or kwargs["name"] is None:
        raise ColorRequired

    if "leverage" in kwargs:
        if not isinstance(kwargs["leverage"], int):
            raise LeverageInvalid(kwargs["leverage"])

    return False


def get_existing_pipeline(fields):
    pipeline = Pipeline.objects.get(**fields)

    if pipeline.active:
        raise DataPipelineOngoing(pipeline.id)
    else:
        pipeline.active = True
        pipeline.open_time = datetime.datetime.now(pytz.utc)

        pipeline.save()

    return pipeline


def get_or_create_pipeline(
    exists,
    pipeline_id,
    name,
    color,
    allocation,
    symbol,
    candle_size,
    strategy,
    exchange,
    params,
    paper_trading,
    leverage
):
    if exists:
        pipeline = get_existing_pipeline(dict(id=pipeline_id))

    else:
        columns = dict(
            name=name,
            color=color,
            allocation=allocation,
            symbol_id=symbol,
            interval=candle_size,
            strategy=strategy,
            exchange_id=exchange,
            params=json.dumps(params),
            paper_trading=paper_trading,
            leverage=leverage
        )

        try:
            pipeline = Pipeline.objects.create(**columns)
            logging.info(f"Successfully created new pipeline ({pipeline.id})")
        except django.db.utils.IntegrityError:
            pipeline = get_existing_pipeline(columns)

    return pipeline


def convert_queryset_to_dict(queryset):
    return {res["name"]: res for res in queryset}


def convert_trades_to_dict(trades_metrics):
    return {
        'numberTrades': trades_metrics['id__count'],
        'maxTradeDuration': trades_metrics['duration__max'].total_seconds() * 1000,
        'avgTradeDuration': trades_metrics['duration__avg'].total_seconds() * 1000,
        'bestTrade': round(trades_metrics['profit_loss__max'], 5),
        'worstTrade': round(trades_metrics['profit_loss__min'], 5),
        'winningTrades': trades_metrics['winning_trade__sum'],
        'losingTrades': trades_metrics['losing_trade__sum'],
    }


def convert_client_request(data):
    return {
        "name": data["name"],
        "allocation": data["allocation"],
        "symbol_id": data["symbol"],
        "strategy": data["strategy"],
        "interval": data["candleSize"],
        "exchange_id": data["exchanges"],
        "params": json.dumps(data["params"]),
        "paper_trading": data["paperTrading"],
        "color": data["color"],
        "leverage": data["leverage"]
    }
