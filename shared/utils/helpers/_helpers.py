import json
import os
import re
from collections import namedtuple

import django

from shared.utils.exceptions import SymbolInvalid, NoSuchPipeline

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline, Symbol

escapes = ''.join([chr(char) for char in range(1, 32)])
translator = str.maketrans('', '', escapes)


PIPELINE = namedtuple(
    'Pipeline',
    [
        "id",
        "symbol",
        "strategy",
        "candle_size",
        "exchange",
        "paper_trading",
        "active",
        "equity",
        "leverage"
    ]
)


def convert_signal_to_text(signal):
    if signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    else:
        return "NEUTRAL"


def get_logging_row_header(pipeline):

    return f"{pipeline.name}|{pipeline.id}|{pipeline.interval}: "


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
        strategy=[obj.as_json() for obj in pipeline.strategy.all()],
        candle_size=pipeline.interval,
        exchange=pipeline.exchange.name,
        paper_trading=pipeline.paper_trading,
        active=pipeline.active,
        equity=pipeline.equity,
        leverage=pipeline.leverage
    )

    return pipeline


def get_extended_name(name):
    re_outer = re.compile(r'([^A-Z ])([A-Z])')
    re_inner = re.compile(r'(?<!^)([A-Z])([^A-Z])')
    return re_outer.sub(r'\1 \2', re_inner.sub(r' \1\2', name))


def clean_docstring(doc):
    return doc.translate(translator).strip()


def get_symbol_or_raise_exception(symbol):
    if not Symbol.objects.filter(name=symbol).exists():
        raise SymbolInvalid(symbol)
    else:
        return Symbol.objects.get(name=symbol)


def get_input_dimensions(lst, n_dim=0):
    """
    Recursively determines the dimensions of a nested list or tuple.

    Parameters:
    -----------
    lst : list or tuple
        The nested list or tuple to determine the dimensions of.
    n_dim : int, optional
        Internal parameter to track the current nesting level (default is 0).

    Returns:
    --------
    int
        The number of dimensions in the nested structure. For a flat list, the
        result is 1. For each level of nesting, the result increases by 1.

    Examples:
    ---------
    >>> get_input_dimensions([1, 2, 3])
    1

    >>> get_input_dimensions([[1, 2], [3, 4]])
    2

    >>> get_input_dimensions([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    3
    """
    if isinstance(lst, (list, tuple)):
        return get_input_dimensions(lst[0], n_dim + 1) if len(lst) > 0 else 0
    else:
        return n_dim
