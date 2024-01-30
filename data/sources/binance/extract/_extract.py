import os
from datetime import datetime

import django
import pandas as pd
import pytz

import shared.exchanges.binance.constants as const
from shared.data.queries import get_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


def get_earliest_date(model_class, symbol, candle_size):
    try:
        earliest_date = model_class.objects \
                         .filter(exchange='binance', symbol=symbol, interval=candle_size) \
                         .order_by('open_time').first().open_time
    except AttributeError:
        earliest_date = datetime.now().astimezone(pytz.utc)

    return earliest_date


def get_latest_date(model_class, symbol, candle_size, upper_date_limit=None):

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
    return start_date + (pd.Timedelta(const.CANDLE_SIZES_MAPPER[candle_size]) * batch_size)


def extract_data(
    get_klines_method,
    symbol,
    candle_size,
    start_date,
    klines_batch_size=1000,
    header=''
):
    """
    Fetches missing data on specified model class and for a
    specific symbol, candle_size and exchange from the Binance API.

    Parameters
    ----------
    model_class: class - required. Database model class to save data on.
    get_klines_method: method - required. Historical data fetching function.
    symbol: str - required. Symbol for which to retrieve data.
    candle_size: str - optional. Candle size at which data should be retrieved.
    klines_batch_size: int - optional. batch size of klines to retrieve on each function call.
    start_date: datetime object - optional. Start date from which to retrieve data.
                If not specified, data will be fetched from the last entry on.
    header: Header for logging line.

    Returns
    -------
    DataFrame with fetched data.

    """
    end_date = get_end_date(start_date, candle_size, klines_batch_size)

    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int(end_date.timestamp() * 1000)

    klines = get_klines_method(symbol, candle_size, start_timestamp, end_timestamp, limit=klines_batch_size)

    data = []
    for kline in klines:

        fields = {field: get_value(kline) for field, get_value in const.BINANCE_KEY.items()}

        data.append(fields)

    return pd.DataFrame(data)


def extract_data_db(exchange_data, model_class, symbol, candle_size, base_candle_size, start_date):
    """
    Extracts data from a database for a given financial instrument.

    Parameters:
    - exchange_data (pd.DataFrame): DataFrame containing exchange data.
    - model_class (str): The class of the financial model.
    - symbol (str): The symbol of the financial instrument.
    - candle_size (str): The size of the candles for the extracted data.
    - base_candle_size (str): The base size of candles for data retrieval.

    Returns:
    pd.DataFrame: A DataFrame containing the extracted data with the index reset.

    Example:
    >>> extract_data_db(exchange_data, MyModel, 'BTCUSDT', '1h', '5m')
    # Returns a DataFrame with extracted data for BTC/USDT using 1-hour candles,
    # starting from the last available data point with 1-day candles.
    """

    data = get_data(exchange_data, start_date, symbol, base_candle_size, exchange='binance')
    return data.reset_index()
