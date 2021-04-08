import os
from datetime import datetime, timedelta

from binance.websockets import BinanceSocketManager
from django.db import connection
import django
import pandas as pd

import database
from shared.exchanges import BinanceHandler
import shared.exchanges.binance.constants as const

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Asset, Symbol, ExchangeData, Exchange


class BinanceDataHandler(BinanceHandler, BinanceSocketManager):

    def __init__(self, base="BTC", quote="USDT", candle_size='5m'):

        BinanceHandler.__init__(self)
        BinanceSocketManager.__init__(self, self)

        self.base = base
        self.quote = quote
        self.symbol = base + quote
        self.exchange = 'binance'
        self.candle_size = candle_size

        self.conn_key = None

        self.data = pd.DataFrame()
        self.data_length = 0

    def start_data_ingestion(self):

        self._get_missing_data()

        self._start_websocket(self.symbol, self.websocket_callback)

    def stop_data_ingestion(self):
        pass

    def _start_websocket(self, symbol, callback, option='kline'):
        print(f"Starting data stream...")

        self.conn_key = getattr(self, f'start_{option}_socket')(symbol=symbol, callback=callback,
                                                                interval=self.candle_size)
        self.start()

    def _stop_websocket(self):
        self.stop_socket(self.conn_key)

    def _get_missing_data(self):

        print(f"Getting historical data up until now ({datetime.utcnow()})...")

        start_date = ExchangeData.objects \
                         .filter(exchange=self.exchange, symbol=self.symbol) \
                         .order_by('open_time').last().open_time - timedelta(hours=6)

        self.get_historical_data(
            self.quote,
            self.base,
            self.KLINE_INTERVAL_1MINUTE,
            int(start_date.timestamp() * 1000)
        )

    def _resample_data(self, aggregation_method):
        self.data = self.data \
            .resample(const.CANDLE_SIZES_MAPPER[self.candle_size]) \
            .agg(aggregation_method) \
            .ffill()[:-1]

    def get_symbol(self, symbol, quote, base):
        try:
            return Symbol.objects.get(name=symbol)
        except database.model.models.Symbol.DoesNotExist:
            quote_asset = Asset.objects.get_or_create(symbol=quote)[0]
            base_asset = Asset.objects.get_or_create(symbol=base)[0]

            obj = Symbol(name=symbol, quote=quote_asset, base=base_asset)
            obj.save()

            return obj

    def get_historical_data(self, quote, base, interval, start_date):

        symbol = base + quote

        klines = self.get_historical_klines_generator(symbol, interval, start_date)

        for i, kline in enumerate(klines):

            fields = {field: get_value(kline) for field, get_value in const.BINANCE_KEY.items()}

            fields.update({
                "exchange": Exchange.objects.get_or_create(name=self.exchange)[0],
                "symbol": self.get_symbol(symbol, quote, base),
                "interval": interval
            })

            try:
                obj = ExchangeData.objects.create(**fields)
            except django.db.utils.IntegrityError:

                unique_fields = {"open_time", "exchange", "symbol", "interval"}

                fields_subset = {key: value for key, value in fields.items() if key in unique_fields}

                ExchangeData.objects.filter(**fields_subset).update(**fields)

            if i % 1E4 == 0:
                print(fields["open_time"])

        ExchangeData.objects.last().delete()

    def websocket_callback(self, row):

        # self.stop_socket(self.conn_key)
        # print(row)

        df = pd.DataFrame(
            {
                const.NAME_MAPPER[key]: [const.FUNCTION_MAPPER[key](value)]
                for key, value in row["k"].items()
                if key in const.NAME_MAPPER
            }
        ).set_index('open_time')

        self.data = self.data.append(df)

        self._resample_data(const.COLUMNS_AGGREGATION_WEBSOCKET)

        if len(self.data) != self.data_length:

            self.data_length = len(self.data)

            last_row = self.data.iloc[-1]

            # TODO: Append this row to Database


if __name__ == "__main__":

    quote = "USDT"
    base = "BTC"

    binance_data_handler = BinanceDataHandler(quote, base)

    # start_date = int(datetime(2021, 3, 23, 12, 33).timestamp() * 1000)
    start_date = int(datetime(2020, 12, 21, 8, 0).timestamp() * 1000)

    binance_data_handler.get_historical_data(quote, base, '5m', start_date)
