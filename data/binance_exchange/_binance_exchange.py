import logging
import os
from datetime import datetime

import pandas as pd
import numpy as np
import django
from binance.websockets import BinanceSocketManager

import shared.exchanges.binance.constants as const
from data.binance.extract import get_missing_data, get_historical_data
from data.binance.load import save_new_entry_db
from data.binance.transform import resample_data
from shared.exchanges import BinanceHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import ExchangeData, StructuredData


class BinanceDataHandler(BinanceHandler, BinanceSocketManager):

    def __init__(self, base="BTC", quote="USDT", candle_size='1h'):

        BinanceHandler.__init__(self)
        BinanceSocketManager.__init__(self, self)

        self.base = base
        self.quote = quote
        self.symbol = base + quote
        self.exchange = 'binance'
        self.candle_size = candle_size

        self.conn_key = {}

        self.raw_data = pd.DataFrame()
        self.data = pd.DataFrame()
        self.raw_data_length = 1
        self.data_length = 1

    def start_data_ingestion(self):

        logging.info(f"Starting data stream...")

        get_missing_data(
            self.get_historical_klines_generator,
            self.base,
            self.quote,
            self.base_candle_size,
            self.exchange
        )

        self._start_kline_websockets(self.symbol, self.websocket_callback)

    def stop_data_ingestion(self):
        logging.info(f"Stopping data stream...")

        self._stop_websocket()

    def _start_kline_websockets(self, symbol, callback):

        streams = [f"{symbol.lower()}@kline_{self.base_candle_size}", f"{symbol.lower()}@kline_{self.candle_size}"]

        self.streams = streams

        self.conn_key = self.start_multiplex_socket(streams, callback)

        self.start()

    def _stop_websocket(self):
        self.close()

    def process_new_data(self, model_class, data, data_length, candle_size):

        new_entries = []
        if len(data) != data_length:

            rows = data.iloc[data_length-1:-1].reset_index()

            data_length = len(data)

            logging.info(f"Added {len(rows)} new rows onto {model_class}")

            for index, row in rows.iterrows():

                new_entry = save_new_entry_db(
                    model_class,
                    row,
                    self.quote,
                    self.base,
                    self.exchange,
                    candle_size
                )

                new_entries.append(new_entry)

        return data, data_length, np.any(new_entries)

    def process_stream(self, model_class, row, data, data_length, candle_size):

        new_data = pd.DataFrame(
            {
                const.NAME_MAPPER[key]: [const.FUNCTION_MAPPER[key](value)]
                for key, value in row.items()
                if key in const.NAME_MAPPER
            }
        ).set_index('open_time')

        # Raw data
        data = data.append(new_data)

        data = resample_data(
            data,
            candle_size,
            const.COLUMNS_AGGREGATION_WEBSOCKET
        )

        return self.process_new_data(
            model_class, data, data_length, candle_size
        )

    def websocket_callback(self, row):

        # self.stop_socket(self.conn_key)
        print(row)

        kline_size = row["stream"].split('_')[-1]

        if kline_size == self.base_candle_size:

            self.raw_data, self.raw_data_length, _ = self.process_stream(
                ExchangeData,
                row["data"]["k"],
                self.raw_data,
                self.raw_data_length,
                self.base_candle_size
            )

        elif kline_size == self.candle_size:

            self.data, self.data_length, new_entry = self.process_stream(
                StructuredData,
                row["data"]["k"],
                self.data,
                self.data_length,
                self.candle_size
            )

            if new_entry:
                # TODO: Notify quant model service that there is new data
                pass


if __name__ == "__main__":

    quote = "USDT"
    base = "BTC"

    symbol = base + quote

    interval = '5m'

    binance_data_handler = BinanceDataHandler(quote, base)

    start_date = int(datetime(2020, 12, 21, 8, 0).timestamp() * 1000)

    get_historical_data(
        binance_data_handler.get_historical_klines_generator,
        base,
        quote,
        'binance',
        interval,
        start_date
    )
