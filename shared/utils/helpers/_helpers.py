import math
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

from database.model.models import Pipeline, Trade as DBTrade

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


def get_root_dir():
    return os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            '../../..'
        )
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


def convert_trade(trade: DBTrade):
    """
    Converts a database Trade object into a standardized Trade object with structured attributes.

    Parameters
    ----------
    trade : Trade object or similar
        The raw trade object containing trade details such as open and close times, prices,
         amount, side, and profit.

    Returns
    -------
    Trade
        A structured Trade object containing the processed information from the db trade.

    """

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
    """
    Calculates the minimum lookback date required based on the maximum window size and the candle size.

    Parameters
    ----------
    max_window : int
        The maximum window size used in strategy calculations, which determines how far back the data
         needs to go.
    candle_size : str
        The size of the candle (e.g., "1h", "1d") which impacts the calculation of the lookback period.

    Returns
    -------
    datetime
        The calculated minimum lookback date as a datetime object, timezone-aware and adjusted to UTC.

    Notes
    -----
    The function uses a multiplier (1.4) to ensure a slightly larger buffer is included in the
     lookback period.
    """
    return (datetime.now().astimezone(pytz.utc) -
            pd.Timedelta(const.CANDLE_SIZES_MAPPER[candle_size]) * max_window * 1.4)


def get_pipeline_max_window(pipeline_id, default_min_rows):
    """
    Determines the maximum window size for a given pipeline by inspecting its strategies and parameters.

    Parameters
    ----------
    pipeline_id : int
        The identifier of the pipeline.
    default_min_rows : int
        The default minimum number of rows to fall back on if no specific value is determined.

    Returns
    -------
    int
        The maximum window size calculated based on the strategy parameters
        within the pipeline, or the default minimum if no specific value is determined.

    Raises
    ------
    Pipeline.DoesNotExist
        If no pipeline with the given `pipeline_id` exists.

    Notes
    -----
    This function is useful for dynamically adjusting the amount of data fetched
    based on the needs of the pipeline's strategies.
    """
    try:
        pipeline = Pipeline.objects.get(id=pipeline_id).as_json()
    except Pipeline.DoesNotExist:
        return int(default_min_rows)

    strategies = pipeline["strategy"]

    max_value_params = 0
    for strategy in strategies:

        try:
            max_value = max([
                value for param, value in strategy["params"].items()
                if isinstance(value, (int, float))
            ])

            if max_value > max_value_params:
                max_value_params = max_value
        except ValueError:
            continue

    return max(max_value_params, int(default_min_rows))


def get_number_of_batches(start_date, candle_size, batch_size, end_date=None):
    """
    Calculates the number of batches needed to fetch historical data based on
    the start date, candle size, and batch size.

    Parameters
    ----------
    start_date : datetime
        The start date from which to begin fetching data.
    candle_size : str
        The granularity of the data, e.g., "1h" for hourly candles.
    batch_size : int
        The number of candles to fetch per batch.
    end_date : datetime
        The end date until which to fetch the data.

    Returns
    -------
    int
        The total number of batches required to fetch all historical data from
        the start date up to the current date.

    Notes
    -----
    This function helps in breaking down large data requests into manageable
    batches to improve performance.
    """
    if end_date is None:
        end_date = datetime.now().astimezone(pytz.utc)

    time_diff = end_date - start_date
    time_slots = time_diff / pd.Timedelta(const.CANDLE_SIZES_MAPPER[candle_size])

    return math.ceil(time_slots / batch_size)


def get_earliest_date(model_class, symbol, candle_size):
    """
    Retrieves the earliest available date for a given symbol and candle size from the database.

    Parameters
    ----------
    model_class : Django model
        The Django model class that represents the structured data in the database.
    symbol : str
        The trading symbol for which to find the earliest available date.
    candle_size : str
        The granularity of the data, e.g., "1h" for hourly data.

    Returns
    -------
    datetime
        The earliest available date for the specified symbol and candle size.

    Notes
    -----
    This function is particularly useful for determining how far back
    historical data is available for a specific trading symbol and data granularity.
    """
    try:
        earliest_date = model_class.objects \
                         .filter(exchange='binance', symbol=symbol, interval=candle_size) \
                         .order_by('open_time').first().open_time
    except AttributeError:
        earliest_date = datetime.now().astimezone(pytz.utc)

    return earliest_date


def get_latest_date(model_class, symbol, candle_size, upper_date_limit=None):
    """
    Fetches the most recent available date for a given symbol and candle size
    from the database, optionally constrained by an upper date limit.

    Parameters
    ----------
    model_class : Django model
        The Django model class representing the structured data in the database.
    symbol : str
        The trading symbol for which to find the latest available date.
    candle_size : str
        The granularity of the data, e.g., "1d" for daily data.
    upper_date_limit : datetime, optional
        An optional upper limit for the date query. If provided, the search for
        the latest date will not exceed this limit.

    Returns
    -------
    datetime
        The most recent available date for the specified symbol and candle size,
        not exceeding the optional upper date limit.

    Notes
    -----
    This function can be used to efficiently query the latest data point
    available before fetching new data or for synchronization purposes.
    """

    query = {
        "symbol": symbol,
        "interval": candle_size,
        "exchange": "binance"
    }

    if upper_date_limit is not None:
        query["open_time__lte"] = upper_date_limit

    try:
        latest_date = model_class.objects.filter(**query).order_by('open_time').last().open_time
    except AttributeError:
        latest_date = upper_date_limit

    return latest_date


def get_end_date(start_date, candle_size, batch_size):
    """
    Calculates the end date for a batch of data based on the start date,
    candle size, and batch size.

    Parameters
    ----------
    start_date : datetime
        The start date from which the batch calculation begins.
    candle_size : str
        The granularity of the data, e.g., "15m" for fifteen-minute data.
    batch_size : int
        The number of data points (candles) to include in the batch.

    Returns
    -------
    datetime
        The end date for the batch, calculated based on the specified parameters.

    Notes
    -----
    This function is used for partitioning large datasets into manageable
    batches, especially when fetching historical data over extended periods.
    """
    return start_date + (pd.Timedelta(const.CANDLE_SIZES_MAPPER[candle_size]) * batch_size)
