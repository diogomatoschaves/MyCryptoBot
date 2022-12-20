import logging
import os

import pandas as pd
import django
import redis
from binance import ThreadedWebsocketManager

import shared.exchanges.binance.constants as const
from data.service.helpers.exceptions import CandleSizeInvalid
from data.sources import trigger_signal
from data.sources.binance.extract import extract_data
from data.sources.binance.load import load_data
from data.sources.binance.transform import resample_data, transform_data
from shared.exchanges.binance import BinanceHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import ExchangeData, StructuredData, Pipeline

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

cache = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))


class BinanceDataHandler(BinanceHandler, ThreadedWebsocketManager):

    """
    Class that handles realtime / incoming data from the Binance API, and
    triggers signal generation whenever a new step has been surpassed (currently
    only time based steps).
    """

    def __init__(self, symbol, candle_size, pipeline_id=None):

        BinanceHandler.__init__(self)
        ThreadedWebsocketManager.__init__(self, self.binance_api_key, self.binance_api_secret)

        self._validate_input(symbol, candle_size)

        self.candle_size = candle_size
        self.pipeline_id = pipeline_id
        self.exchange = 'binance'

        self.conn_key = ''
        self.streams = []

        self.raw_data = pd.DataFrame()
        self.data = pd.DataFrame()
        self.raw_data_length = 1
        self.data_length = 1

        self.start()
        self.started = True

    def __str__(self):
        return self.__name__

    def _validate_input(self, symbol, candle_size):
        """
        Checks if requested symbol exists.

        Parameters
        ----------
        symbol : str
                 initialized symbol to check validity of.

        Returns
        -------
        sets instance parameters: symbol, quote, base

        """
        symbol_info = self.validate_symbol(symbol)

        if candle_size not in const.CANDLE_SIZES_MAPPER:
            raise CandleSizeInvalid(candle_size)

        self.symbol = symbol
        self.base = symbol_info["baseAsset"],
        self.quote = symbol_info["quoteAsset"],

    def start_data_ingestion(self, header=''):
        """
        Public method which sets in motion the data pipeline for a given symbol.

        Returns
        -------
        None

        """

        # Get missing raw data
        self._etl_pipeline(ExchangeData, self.base_candle_size, count_updates=False, header=header)

        # Get missing structured data
        self._etl_pipeline(
            StructuredData,
            self.candle_size,
            remove_zeros=True,
            remove_rows=True,
            count_updates=False,
            header=header
        )

        self.generate_new_signal(header)

        self._start_kline_websockets(self.symbol, self._websocket_callback, header=header)

    # TODO: Refactor to allow for more than one conn_key
    def stop_data_ingestion(self, header=''):
        """
        Public method which stops the data pipeline for the symbol.

        Returns
        -------
        None

        """
        logging.info(header + f"Stopping {', '.join(self.streams)} data stream(s).")

        self._stop_websocket()

        ExchangeData.objects.filter(symbol=self.symbol, exchange_id=self.exchange).last().delete()
        StructuredData.objects.filter(symbol=self.symbol, exchange_id=self.exchange).last().delete()

    def _start_kline_websockets(self, symbol, callback, header=''):

        # streams = [
        #     f"{symbol.lower()}_perpetual@continuousKline_{self.base_candle_size}",
        #     f"{symbol.lower()}_perpetual@continuousKline_{self.candle_size}"
        # ]

        streams = [
            f"{symbol.lower()}@kline_{self.base_candle_size}",
            f"{symbol.lower()}@kline_{self.candle_size}"
        ]

        logging.info(header + f"Starting {', '.join(streams)} data stream(s).")

        self.streams = streams

        self.conn_key = self.start_multiplex_socket(lambda row: callback(row, header), streams)

    # TODO: Wrap this in AttributeError exception handling
    def _stop_websocket(self):
        self.stop_socket(self.conn_key)

    def _etl_pipeline(
        self,
        model_class,
        candle_size,
        reference_candle_size='5m',
        data=None,
        remove_zeros=False,
        remove_rows=False,
        columns_aggregation=const.COLUMNS_AGGREGATION,
        count_updates=True,
        header=''
    ):

        # Extract
        if data is None:
            data = extract_data(model_class, self.get_historical_klines_generator, self.symbol,
                                self.base_candle_size, candle_size, header=header)

        # Transform
        data = transform_data(
            data,
            candle_size,
            self.exchange,
            self.symbol,
            reference_candle_size=reference_candle_size,
            aggregation_method=columns_aggregation,
            is_removing_zeros=remove_zeros,
            is_removing_rows=remove_rows,
            header=header
        )

        # Load
        new_entries = load_data(model_class, data, count_updates=count_updates)

        logging.info(header + f"Added {new_entries} new rows into {model_class}.")

        return new_entries

    def generate_new_signal(self, header):

        success = trigger_signal(self.pipeline_id, header=header)

        if not success:
            logging.warning(
                header +
                "There was an error processing the signal generation request. Stopping data pipeline."
            )
            self.stop_data_ingestion()
            # TODO: Should close all positions associated with pipeline
            Pipeline.objects.filter(id=self.pipeline_id).update(active=False)

    # TODO: Add timer to check if it's below 24h
    def _websocket_callback(self, row, header=''):

        logging.info(row)

        kline_size = row["stream"].split('_')[-1]

        if kline_size == self.base_candle_size:
            self.raw_data, self.raw_data_length, _ = self._process_stream(
                ExchangeData,
                row["data"]["k"],
                self.raw_data,
                self.raw_data_length,
                self.base_candle_size
            )

        if kline_size == self.candle_size:
            self.data, self.data_length, new_entry = self._process_stream(
                StructuredData,
                row["data"]["k"],
                self.data,
                self.data_length,
                self.candle_size,
                remove_zeros=True,
                remove_rows=True,
            )

            if new_entry:
                self.generate_new_signal(header)

    def _process_stream(
        self,
        model_class,
        row,
        data,
        data_length,
        candle_size,
        remove_zeros=False,
        remove_rows=False,
    ):

        new_data = pd.DataFrame(
            {
                const.NAME_MAPPER[key]: [const.FUNCTION_MAPPER[key](value)]
                for key, value in row.items()
                if key in const.NAME_MAPPER
            }
        ).set_index('open_time')

        data = data.append(new_data)

        data = resample_data(
            data,
            candle_size,
            const.COLUMNS_AGGREGATION_WEBSOCKET
        )

        return self._process_new_data(
            model_class,
            data,
            data_length,
            candle_size,
            remove_zeros=remove_zeros,
            remove_rows=remove_rows
        )

    def _process_new_data(
        self,
        model_class,
        data,
        data_length,
        candle_size,
        remove_zeros=False,
        remove_rows=False
    ):
        new_entries = 0
        if len(data) != data_length:

            rows = data.iloc[data_length-1:-1].reset_index()

            data_length = len(data)

            new_entries = self._etl_pipeline(
                model_class,
                candle_size,
                reference_candle_size=candle_size,
                data=rows,
                remove_zeros=remove_zeros,
                remove_rows=remove_rows,
                columns_aggregation=const.COLUMNS_AGGREGATION
            )

        return data, data_length, new_entries > 0
