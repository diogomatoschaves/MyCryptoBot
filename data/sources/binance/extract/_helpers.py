import math
import os
from datetime import datetime

import django
import pandas as pd
import pytz

from shared.data.queries import get_data
from shared.exchanges.binance import constants as const
from shared.exchanges.binance.constants import CANDLE_SIZES_MAPPER
from shared.utils.config_parser import get_config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import ExchangeData


config_vars = get_config('data')


def get_missing_dates(start_date, symbol, end_date=None):
    """
    Identifies missing datetime entries in the market data for a given symbol and candle
     size between a specified start and end date.

    Parameters
    ----------
    start_date : datetime
        The start date of the period for which to check for missing data. Must have tzinfo set.
    symbol : str
        The market symbol (e.g., "BTCUSDT") for which to check for missing data.
    end_date : datetime, optional
        The end date of the period for which to check for missing data.
        If None, defaults to the current date and time.

    Returns
    -------
    pd.DatetimeIndex
        An index of datetime objects representing the missing dates and times in the specified range.

    Raises
    ------
    KeyError
        If `base_candle_size` does not correspond to a valid key in `CANDLE_SIZES_MAPPER`.
    """

    start_date = round_date(start_date, config_vars.base_candle_size)

    data = get_data(ExchangeData, start_date, symbol, config_vars.base_candle_size, exchange='binance')

    if end_date is None:
        end_date = datetime.now(tz=pytz.utc)

    freq = CANDLE_SIZES_MAPPER[config_vars.base_candle_size]

    datetime_index = pd.date_range(start_date, end_date, freq=freq)

    missing_dates = datetime_index[~datetime_index.isin(data.index)]

    return missing_dates


def get_earliest_missing_date(start_date, symbol, end_date=None):
    """
    Finds the earliest date and time within a specified date range for which market data is
     missing for a given symbol and candle size. If all dates are present, returns None.

    Parameters
    ----------
    start_date : str or datetime
        The start date of the period for which to check for missing data, in 'YYYY-MM-DD'
        format or as a datetime object.
    symbol : str
        The trading symbol (e.g., "BTCUSDT") for which to check for missing data.
    end_date : str or datetime, optional
        The end date of the period for which to check for missing data, in 'YYYY-MM-DD'
        format or as a datetime object. Defaults to the current date and time if None.

    Returns
    -------
    datetime or None
        The earliest datetime for which market data is missing within the specified range,
        or None if there are no missing dates.

    Examples
    --------
    >>> earliest_missing_date = get_earliest_missing_date("2021-01-01", "BTCUSDT", "1h", "2021-01-10")
    >>> print(earliest_missing_date)
    This will print the earliest missing hourly data point for BTCUSDT between 2021-01-01 and 2021-01-10, if any.
    If all data points are present, it prints None.

    Notes
    -----
    - The function first retrieves a list of missing dates using `get_missing_dates` and then checks
    if this list is empty. If not empty, the first element (earliest missing date) is returned;
    otherwise, None is returned, indicating complete data coverage within the specified range.
    """

    if isinstance(start_date, str):
        start_date = pd.Timestamp(start_date, tzinfo=pytz.utc)

    if isinstance(end_date, str):
        end_date = pd.Timestamp(end_date, tzinfo=pytz.utc)

    missing_dates = get_missing_dates(start_date, symbol, end_date)

    return missing_dates[0] if len(missing_dates) > 0 else None


def round_date(date, timeframe='5m'):
    if timeframe == '5m':
        return date.replace(
            minute=date.minute - date.minute % 5,
            second=0,
            microsecond=0
        )


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
