import os
from collections import namedtuple
from datetime import datetime

import django
import pandas as pd
import pytz
from stratestic.backtesting.helpers import Trade

from shared.exchanges.binance import constants as const
from shared.utils.exceptions import NoSuchPipeline

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline

escapes = ''.join([chr(char) for char in range(1, 32)])
translator = str.maketrans('', '', escapes)


PIPELINE = namedtuple(
    'Pipeline',
    [
        "id",
        "symbol",
        "strategy",
        "strategy_combination",
        "candle_size",
        "exchange",
        "paper_trading",
        "active",
        "initial_equity",
        "current_equity",
        "leverage"
    ]
)


def get_logging_row_header(pipeline):

    return f"{pipeline.name}|{pipeline.id}|{pipeline.interval}: "


def get_item_from_cache(cache, key):

    item = cache.get(f"pipeline {key}")

    return item if item else '""'


def get_pipeline_data(pipeline_id, return_obj=False):
    try:
        pipeline = Pipeline.objects.get(id=pipeline_id)
    except Pipeline.DoesNotExist:
        raise NoSuchPipeline(pipeline_id)

    if return_obj:
        return pipeline
    else:
        pipeline = PIPELINE(
            id=pipeline_id,
            symbol=pipeline.symbol.name,
            strategy=[obj.as_json() for obj in pipeline.strategy.all()],
            strategy_combination=pipeline.strategy_combination,
            candle_size=pipeline.interval,
            exchange=pipeline.exchange.name,
            paper_trading=pipeline.paper_trading,
            active=pipeline.active,
            initial_equity=pipeline.initial_equity,
            current_equity=pipeline.current_equity,
            leverage=pipeline.leverage
        )

        return pipeline


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


def convert_trade(trade):
    return Trade(
        entry_date=trade.open_time,
        exit_date=trade.close_time,
        entry_price=trade.open_price,
        exit_price=trade.close_price,
        units=trade.amount,
        side=trade.side,
        profit=trade.pnl,
        pnl=trade.pnl_pct
    )


def get_minimum_lookback_date(max_window, candle_size):
    return (datetime.now().astimezone(pytz.utc) -
            pd.Timedelta(const.CANDLE_SIZES_MAPPER[candle_size]) * max_window * 1.4)


def get_pipeline_max_window(pipeline_id):
    try:
        strategies = Pipeline.objects.get(id=pipeline_id).as_json()["strategy"]

        max_value_params = 0
        for strategy in strategies:
            try:
                max_value = max([value for param, value in strategy["params"].items()])
            except ValueError:
                continue

            if max_value > max_value_params:
                max_value_params = max_value

        return max_value_params
    except Pipeline.DoesNotExist:
        return 1000