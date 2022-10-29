import json
import os
import re
from collections import namedtuple

import django

from shared.utils.exceptions import SymbolInvalid, NoSuchPipeline

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline


PIPELINE = namedtuple(
    'Pipeline',
    [
        "id",
        "symbol",
        "strategy",
        "params",
        "candle_size",
        "exchange",
        "paper_trading",
        "active"
    ]
)


def convert_signal_to_text(signal):
    if signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    else:
        return "NEUTRAL"


def get_logging_row_header(symbol, strategy, params, candle_size, exchange, paper_trading):

    paper_trading_str = "LIVE" if not paper_trading else "FAKE"

    return f"{paper_trading_str}|{symbol}|{strategy}&{params}|{candle_size}|{exchange}: "


def get_item_from_cache(cache, key):

    item = cache.get(f"pipeline {key}")

    return item if item else '""'


def get_pipeline_data(pipeline_id):
    try:
        pipeline = Pipeline.objects.get(id=pipeline_id)
    except Pipeline.DoesNotExist:
        raise NoSuchPipeline(pipeline_id)

    pipeline = PIPELINE(
        id=pipeline_id,
        symbol=pipeline.symbol.name,
        strategy=pipeline.strategy,
        params=json.loads(pipeline.params),
        candle_size=pipeline.interval,
        exchange=pipeline.exchange.name,
        paper_trading=pipeline.paper_trading,
        active=pipeline.active
    )

    return pipeline


def get_extended_name(name):
    re_outer = re.compile(r'([^A-Z ])([A-Z])')
    re_inner = re.compile(r'(?<!^)([A-Z])([^A-Z])')
    return re_outer.sub(r'\1 \2', re_inner.sub(r' \1\2', name))


def get_symbol_or_raise_exception(exchange_info, symbol):
    symbol_info = None
    for info in exchange_info["symbols"]:
        if info['symbol'] == symbol:
            symbol_info = info

    if not symbol_info:
        raise SymbolInvalid(symbol)

    return symbol_info
