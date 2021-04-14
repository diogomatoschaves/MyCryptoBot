import logging
import os
from datetime import datetime, timedelta

import django
import pandas as pd
import pytz
from requests import ReadTimeout, ConnectionError

import shared.exchanges.binance.constants as const

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


def fetch_missing_data(model_class, klines_generator, symbol, base_candle_size, candle_size, start_date=None):
    """
    Fetches missing data on specified model class and for a
    specific symbol, candle_size and exchange.

    Parameters
    ----------
    model_class: class - required. Database model class to save data on.
    klines_generator: method - required. Historical data fetching function.
    symbol: str - required. Symbol for which to retrieve data.
    base_candle_size: str - required. Candle size at which raw data is retrieved.
    candle_size: str - optional. Candle size at which data should be retrieved.
    start_date: datetime object - optional. Start date from which to retrieve data.
                If not specified, data will be fetched from the last entry on.

    Returns
    -------
    DataFrame with fetched data.

    """
    logging.info(f"{symbol}: Fetching missing historical data.")

    if not start_date:
        try:
            start_date = model_class.objects \
                 .filter(exchange='binance', symbol=symbol, interval=candle_size) \
                 .order_by('open_time').last().open_time - timedelta(hours=6)
        except AttributeError:
            start_date = datetime(2019, 9, 1).astimezone(pytz.utc)

    return get_historical_data(klines_generator, symbol, base_candle_size, int(start_date.timestamp() * 1000))


def get_historical_data(klines_generator, symbol, candle_size, start_date):
    """
    Fetches missing data on specified model class and for a
    specific symbol, candle_size from the Binance API.

    Parameters
    ----------
    klines_generator: method - required. Historical data fetching function.
    symbol: str - required. Symbol for which to retrieve data.
    candle_size: str - optional. Candle size at which data should be retrieved.
    start_date: datetime object - optional. Start date from which to retrieve data.
                If not specified, data will be fetched from the last entry on.

    Returns
    -------
    DataFrame with fetched data.

    """

    klines = klines_generator(symbol, candle_size, start_date)

    data = []
    for i, kline in enumerate(klines):

        retries = 0
        while True:
            try:
                fields = {field: get_value(kline) for field, get_value in const.BINANCE_KEY.items()}
                data.append(fields)
                break
            except (ReadTimeout, ConnectionError) as e:
                logging.warning(e)

                retries += 1
                if retries > 2:
                    raise ConnectionError(e)

        if i % 1E3 == 0:
            logging.debug(f"{symbol}: Processed {i} new rows.")

    return pd.DataFrame(data)
