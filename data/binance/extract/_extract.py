import os
from datetime import datetime, timedelta

import django

import shared.exchanges.binance.constants as const
from data.binance.load import save_new_entry_db

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import ExchangeData


def get_missing_data(klines_generator, base, quote, interval, exchange='binance'):
    print(f"Getting historical data up until now ({datetime.utcnow()})...")

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

    for i, kline in enumerate(klines):

        fields = {field: get_value(kline) for field, get_value in const.BINANCE_KEY.items()}

        save_new_entry_db(fields, quote, base, exchange, interval)

        if i % 1E4 == 0:
            print(fields["open_time"])

    ExchangeData.objects.last().delete()
