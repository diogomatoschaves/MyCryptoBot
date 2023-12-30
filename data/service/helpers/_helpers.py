import datetime
import json
import logging
import os

import django
import pandas as pd
import pytz
from django.db.models import F, Count, Max, Avg, Min, Sum, Q

from data.service.helpers.exceptions import *
from data.service.helpers.exceptions.data_pipeline_ongoing import DataPipelineOngoing
from shared.utils.exceptions import SymbolInvalid, EquityRequired, EquityInvalid, StrategyInvalid, StrategyRequired

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Exchange, Pipeline, Symbol, PortfolioTimeSeries, Strategy, Trade
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


def check_input(strategies, **kwargs):

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
        strategy_input = kwargs["strategy"]

        if strategy_input is None:
            raise StrategyRequired

        if not isinstance(strategy_input, (list, tuple)):
            raise StrategyInvalid(strategy_input)

        for strategy in strategy_input:

            try:
                strategy_name = strategy["name"]
            except KeyError:
                raise StrategyInvalid(strategy_input)

            if strategy_name in strategies:

                try:
                    params = strategy["params"]
                except KeyError:
                    params = {}

                invalid_params = []
                for key in params:
                    if (key not in strategies[strategy_name]["params"]
                            and key not in strategies[strategy_name]["optionalParams"]):
                        logging.debug(key)
                        invalid_params.append(key)

                if len(invalid_params) > 0:
                    raise ParamsInvalid(', '.join(invalid_params))

                required_params = []
                for param in strategies[strategy_name]["params"]:
                    if param not in params:
                        required_params.append(param)

                if len(required_params) > 0:
                    raise ParamsRequired(', '.join(required_params))
            else:
                raise StrategyInvalid(strategy_input)

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

    if "equity" not in kwargs or kwargs["equity"] is None:
        raise EquityRequired
    else:
        equity = kwargs["equity"]

        if not isinstance(equity, (int, float)):
            raise EquityInvalid(equity)

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


def add_strategies(strategies):
    strategies_objs = []
    for strategy in strategies:
        strategy_obj = Strategy.objects.create(name=strategy["name"], params=json.dumps(strategy["params"]))
        strategies_objs.append(strategy_obj)

    return strategies_objs


def get_or_create_pipeline(
    exists,
    pipeline_id,
    strategy,
    data
):

    if exists:
        pipeline = get_existing_pipeline(dict(id=pipeline_id))

    else:
        try:
            pipeline = Pipeline.objects.create(**data)
            strategy_objs = add_strategies(strategy)
            pipeline.strategy.add(*strategy_objs)

            logging.info(f"Successfully created new pipeline ({pipeline.id})")
        except django.db.utils.IntegrityError:
            pipeline = get_existing_pipeline(data)

    return pipeline


def convert_queryset_to_dict(queryset):
    return {res["name"]: res for res in queryset}


def convert_trades_to_dict(trades_metrics):
    return {
        'numberTrades': trades_metrics['id__count'],
        'maxTradeDuration': trades_metrics['duration__max'].total_seconds() * 1000
        if trades_metrics['duration__max'] else None,
        'avgTradeDuration': trades_metrics['duration__avg'].total_seconds() * 1000
        if trades_metrics['duration__avg'] else None,
        'bestTrade': round(trades_metrics['profit_loss__max'], 5) if trades_metrics['profit_loss__max'] else None,
        'worstTrade': round(trades_metrics['profit_loss__min'], 5) if trades_metrics['profit_loss__min'] else None,
        'winningTrades': trades_metrics['winning_trade__sum'],
        'losingTrades': trades_metrics['losing_trade__sum'],
    }


def convert_client_request(data):
    return {
        "name": data["name"],
        "symbol_id": data["symbol"],
        "interval": data["candle_size"].lower(),
        "exchange_id": data["exchange"].lower(),
        "paper_trading": data["paper_trading"],
        "color": data["color"],
        "equity": data["equity"],
        "leverage": data["leverage"],
        "balance": data["equity"] * data["leverage"]
    }


def extract_request_params(request):
    data = request.get_json(force=True)

    pipeline_id = data.get("pipelineId", None)
    name = data.get("name", None)
    color = data.get("color", None)
    equity = data.get("equity", None)
    symbol = data.get("symbol", None)
    strategy = data.get("strategy", None)
    candle_size = data.get("candleSize", None)
    exchange = data.get("exchanges", None)
    paper_trading = data.get("paperTrading") if type(data.get("paperTrading")) == bool else False
    leverage = data.get("leverage", 1)

    return dict(
        pipeline_id=pipeline_id,
        name=name,
        color=color,
        equity=equity,
        symbol=symbol,
        strategy=strategy,
        candle_size=candle_size,
        exchange=exchange,
        leverage=leverage,
        paper_trading=paper_trading
    )


def get_pipeline_equity_timeseries(pipeline_id=None, account_type=None, time_frame_converted='1H'):

    if pipeline_id is not None:
        timeseries = PortfolioTimeSeries.objects.filter(pipeline__id=pipeline_id).values('time', 'value')

        print(PortfolioTimeSeries.objects.all())
    else:
        timeseries = PortfolioTimeSeries.objects.filter(type=account_type).values('time', 'value')

    if len(timeseries) == 0:
        return []

    df = pd.DataFrame(timeseries).set_index('time').rename(columns={"value": "$"})
    df = df.resample(time_frame_converted).first().ffill().reset_index()

    return json.loads(df.to_json(orient='records'))


def query_trades_metrics(pipeline=None):

    if pipeline:
        qs = pipeline.trade_set.exclude(close_time=None)
    else:
        qs = Trade.objects.exclude(close_time=None)

    return qs.annotate(
        duration=F('close_time') - F('open_time'),
        winning_trade=Count('profit_loss', filter=Q(profit_loss__gte=0)),
        losing_trade=Count('profit_loss', filter=Q(profit_loss__lt=0))
    ).aggregate(
        Max('duration'),
        Avg('duration'),
        Count('id'),
        Max('profit_loss'),
        Min('profit_loss'),
        Sum('winning_trade'),
        Sum('losing_trade'),
    )
