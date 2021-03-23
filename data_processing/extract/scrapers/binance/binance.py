import os
import pytz
from os import environ as env
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from binance.client import Client
import django

import database

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

import trading_automation.binance.constants as constants
from database.model.models import Asset, Symbol, ExchangeData, Exchange


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


binance_key = {
    "open_time": lambda x: datetime.fromtimestamp(x[0] / 1000).astimezone(pytz.timezone('UTC')),
    "close_time": lambda x: datetime.fromtimestamp(x[6] / 1000).astimezone(pytz.timezone('UTC')),
    "open": lambda x: x[1],
    "high": lambda x: x[2],
    "low": lambda x: x[3],
    "close": lambda x: x[4],
    "volume": lambda x: x[5],
    "quote_volume": lambda x: x[7],
    "trades": lambda x: x[8],
    "taker_buy_asset_volume": lambda x: x[9],
    "taker_buy_quote_volume": lambda x: x[10],
}


def get_symbol(symbol, quote, base):

    try:
        return Symbol.objects.get(name=symbol)
    except database.model.models.Symbol.DoesNotExist:
        quote_asset = Asset.objects.get_or_create(symbol=quote)[0]
        base_asset = Asset.objects.get_or_create(symbol=base)[0]

        obj = Symbol(name=symbol, quote=quote_asset, base=base_asset)
        obj.save()

        return obj


def get_historical_data(exchange_name, client, quote, base, interval, start_date):

    symbol = quote + base

    klines = client.get_historical_klines_generator(symbol, interval, start_date)

    for i, kline in enumerate(klines):

        fields = {field: get_value(kline) for field, get_value in binance_key.items()}

        fields.update({
            "exchange": Exchange.objects.get_or_create(name=exchange_name)[0],
            "symbol": get_symbol(symbol, quote, base),
            "interval": interval
        })

        if not ExchangeData.objects.filter(exchange=fields["exchange"], open_time=fields["open_time"]).exists():
            obj = ExchangeData(**fields)
            obj.save()

        if i % 1E4 == 0:
            print(fields["open_time"])


if __name__ == "__main__":

    binance_api_key = env.get(constants.BINANCE_API_KEY)
    binance_api_secret = env.get(constants.BINANCE_API_SECRET)

    client = Client(binance_api_key, binance_api_secret)

    quote = "BTC"
    base = "USDT"

    exchange_name = 'binance'

    # start_date = int(datetime(2021, 3, 23, 12, 33).timestamp() * 1000)
    start_date = datetime.utcnow()

    get_historical_data(exchange_name, client, quote, base, client.KLINE_INTERVAL_1MINUTE, start_date)
