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


def fetch_missing_data(
    model_class,
    klines_generator,
    symbol,
    base_candle_size,
    candle_size,
    exchange='binance',
    start_date=None,
):
    logging.info(f"{symbol}: Fetching missing historical data.")

    if not start_date:
        try:
            start_date = model_class.objects \
                 .filter(exchange=exchange, symbol=symbol, interval=candle_size) \
                 .order_by('open_time').last().open_time - timedelta(hours=6)
        except AttributeError:
            start_date = datetime(2019, 9, 1).astimezone(pytz.utc)

    return get_historical_data(klines_generator, symbol, base_candle_size, int(start_date.timestamp() * 1000))


def get_historical_data(klines_generator, symbol, candle_size, start_date):

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
