import logging
import os
from datetime import datetime, timedelta

import django

import shared.exchanges.binance.constants as const
from data.binance_exchange.load import save_new_entry_db

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import ExchangeData


def get_missing_data(klines_generator, base, quote, interval, exchange='binance'):
    logging.info(f"Getting historical data up until now ({datetime.utcnow()})...")

    symbol = base + quote

    start_date = ExchangeData.objects \
                     .filter(exchange=exchange, symbol=symbol) \
                     .order_by('open_time').last().open_time - timedelta(hours=6)

    get_historical_data(
        klines_generator,
        base,
        quote,
        exchange,
        interval,
        int(start_date.timestamp() * 1000)
    )


def get_historical_data(klines_generator, base, quote, exchange, interval, start_date):

    symbol = base + quote

    klines = klines_generator(symbol, interval, start_date)

    new_rows = 0

    for i, kline in enumerate(klines):

        fields = {field: get_value(kline) for field, get_value in const.BINANCE_KEY.items()}

        new_entry = save_new_entry_db(
            ExchangeData,
            fields,
            quote,
            base,
            exchange,
            interval
        )

        if new_entry:
            new_rows += 1

        if i % 1E4 == 0:
            logging.info(fields["open_time"])

    logging.info(f"Added {new_rows - 1} new rows.")

    # ExchangeData.objects.last().delete()
