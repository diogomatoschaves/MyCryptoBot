import json
import os
from collections import namedtuple

import django

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


def get_logging_row_header(symbol, strategy, params, candle_size, exchange):
    return f"{symbol}|{strategy}|{params}|{candle_size}|{exchange}: "


def get_item_from_cache(cache, key):

    item = cache.get(f"pipeline {key}")

    cache.set("dict", "1234")
    print(cache.get("dict"))

    print(item)

    return item if item else '""'


def get_pipeline_data(pipeline_id):
    try:
        pipeline = Pipeline.objects.get(id=pipeline_id)
    except Pipeline.DoesNotExist:
        return None, None

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

    return True, pipeline
