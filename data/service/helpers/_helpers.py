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
from shared.utils.exceptions.leverage_invalid import LeverageInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Exchange, Pipeline, Symbol, PortfolioTimeSeries, Strategy, Trade, \
    strategy_combination_methods
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


def check_input(strategies, edit_pipeline=False, **kwargs):

    pipeline_id = kwargs.get('pipeline_id')
    if not edit_pipeline and Pipeline.objects.filter(id=pipeline_id).exists():
        return True

    symbol = kwargs.get('symbol')
    if symbol is None:
        raise SymbolRequired
    if not Symbol.objects.filter(name=symbol).exists():
        raise SymbolInvalid(symbol)

    exchange = kwargs.get('exchange')
    if exchange is None:
        raise ExchangeRequired
    try:
        Exchange.objects.get(name=exchange.lower())
    except (Exchange.DoesNotExist, AttributeError) as e:
        raise ExchangeInvalid(exchange)

    candle_size = kwargs.get('candle_size')
    if candle_size is None:
        raise CandleSizeRequired
    if candle_size not in const.CANDLE_SIZES_MAPPER:
        raise CandleSizeInvalid(candle_size)

    strategy_input = kwargs.get('strategy')
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

    strategy_combination_method = kwargs.get('strategy_combination_method')
    if strategy_combination_method is not None and \
        (not isinstance(strategy_combination_method, str) or
         strategy_combination_method not in strategy_combination_methods):
        raise StrategyCombinationInvalid(strategy_combination_method)

    name = kwargs.get('name')
    if name is None:
        raise NameRequired
    if (not isinstance(name, str)
            or Pipeline.objects.exclude(id=pipeline_id).exclude(deleted=True).filter(name=name).exists()):

        raise NameInvalid(name)

    color = kwargs.get('color')
    if color is None or name is None:
        raise ColorRequired

    leverage = kwargs.get('leverage')
    if "leverage" in kwargs and not isinstance(leverage, int):
        raise LeverageInvalid(leverage)

    equity = kwargs.get('equity')
    if equity is None:
        raise EquityRequired
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
        strategy_obj = Strategy.objects.create(name=strategy["className"], params=json.dumps(strategy["params"]))
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
        'bestTrade': round(trades_metrics['pnl_pct__max'], 5) if trades_metrics['pnl_pct__max'] else None,
        'worstTrade': round(trades_metrics['pnl_pct__min'], 5) if trades_metrics['pnl_pct__min'] else None,
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
        "initial_equity": data["equity"],
        "leverage": data["leverage"],
        "strategy_combination": data["strategy_combination_method"]
    }


def extract_request_params(request):
    data = request.get_json(force=True)

    pipeline_id = data.get("pipelineId", None)
    name = data.get("name", None)
    color = data.get("color", None)
    equity = data.get("equity", None)
    symbol = data.get("symbol", None)
    strategy = data.get("strategy", None)
    strategy_combination_method = data.get("strategyCombination", 'Majority')
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
        strategy_combination_method=strategy_combination_method,
        candle_size=candle_size,
        exchange=exchange,
        leverage=leverage,
        paper_trading=paper_trading
    )


def resample_equity_data(df, timeframes, max_size):

    original_size = df.shape[0]

    timeframe = list(timeframes)[0]

    for timeframe in timeframes:
        df = df.resample(timeframe).mean().ffill()

        if df.shape[0] > max_size or df.shape[0] > original_size:
            continue

        else:
            break

    return df, timeframe


def add_current_timestamp(df, time_frame):

    now = pd.Timestamp(datetime.datetime.now(tz=pytz.utc)).round(time_frame) - pd.Timedelta(time_frame)

    df_now = pd.DataFrame(data={df.columns[0]: [None], "time": [now]}).set_index('time')

    df = pd.concat([df, df_now], axis=0)

    return df.ffill()


def get_pipeline_equity_timeseries(pipeline_id=None, account_type=None, max_items=500):

    if pipeline_id is not None:
        timeseries = PortfolioTimeSeries.objects.filter(pipeline__id=pipeline_id).values('time', 'value')
    else:
        timeseries = PortfolioTimeSeries.objects.filter(type=account_type).values('time', 'value')

    if len(timeseries) == 0:
        return []

    df = pd.DataFrame(timeseries).set_index('time').rename(columns={"value": "$"})

    df, timeframe = resample_equity_data(df, const.CANDLE_SIZES_MAPPER.values(), max_items)

    df = add_current_timestamp(df, timeframe)

    df = df.reset_index()

    return json.loads(df.to_json(orient='records'))


def query_trades_metrics(pipeline=None):

    if pipeline:
        qs = pipeline.trade_set.exclude(close_time=None)
    else:
        qs = Trade.objects.exclude(close_time=None)

    return qs.annotate(
        duration=F('close_time') - F('open_time'),
        winning_trade=Count('pnl_pct', filter=Q(pnl_pct__gte=0)),
        losing_trade=Count('pnl_pct', filter=Q(pnl_pct__lt=0))
    ).aggregate(
        Max('duration'),
        Avg('duration'),
        Count('id'),
        Max('pnl_pct'),
        Min('pnl_pct'),
        Sum('winning_trade'),
        Sum('losing_trade'),
    )
