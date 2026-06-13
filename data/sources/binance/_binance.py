import logging
import os
from datetime import datetime

import pandas as pd
import pytz
import django
import redis
from binance import ThreadedWebsocketManager
import progressbar

from data.service.external_requests import start_stop_symbol_trading
from data.service.helpers.exceptions import CandleSizeInvalid, DataPipelineCouldNotBeStopped
from data.service.blueprints.bots_api import stop_pipeline
from data.sources import trigger_signal
from data.sources.binance.extract import (
    extract_data,
    extract_data_db,
    get_earliest_missing_date,
    get_number_of_batches,
    get_end_date
)
from data.sources.binance.load import load_data
from data.sources.binance.transform import resample_data, transform_data
from shared.utils.helpers import get_minimum_lookback_date, get_pipeline_max_window, remove_pipeline_loading
from shared.utils.events import publish_pipeline_event, EVENT_DEACTIVATED
from shared.utils.notifier import send_alert
from shared.exchanges.binance import BinanceHandler
from shared.utils.settings import settings
import shared.exchanges.binance.constants as const

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import ExchangeData, StructuredData, Pipeline, Position

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


cache = redis.from_url(settings.redis_url)


class BinanceDataHandler(BinanceHandler, ThreadedWebsocketManager):
    """
    Class that handles realtime / incoming data from the Binance API, and
    triggers signal generation whenever a new step has been surpassed (currently
    only time based steps).
    """

    def __init__(self, symbol, candle_size, pipeline_id=None, start_date=None):

        BinanceHandler.__init__(self, base_candle_size=settings.base_candle_size)
        ThreadedWebsocketManager.__init__(self, self.binance_api_key, self.binance_api_secret)

        self._validate_input(symbol, candle_size)

        self.candle_size = candle_size
        self.pipeline_id = pipeline_id
        self.exchange = 'binance'
        self.header = ''

        self.conn_key = ''
        self.streams = []

        self.start_date = start_date
        self.batch_size = 1000

        self.raw_data = pd.DataFrame()
        self.data = pd.DataFrame()
        self.raw_data_length = 1
        self.data_length = 1

        self.start()
        self.started = True

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
        symbol_obj = self.validate_symbol(symbol)

        if candle_size not in const.CANDLE_SIZES_MAPPER:
            raise CandleSizeInvalid(candle_size)

        self.symbol = symbol
        self.base = symbol_obj.base,
        self.quote = symbol_obj.quote,

    def start_data_ingestion(self, header=''):
        """
        Public method which sets in motion the data pipeline for a given symbol.

        Returns
        -------
        None

        """

        self.header = header

        data = pd.DataFrame()

        self.delete_last_entry()

        start_date = self.get_start_date()

        if start_date is None:
            nr_batches = 0
        else:
            nr_batches = get_number_of_batches(start_date, self.base_candle_size, self.batch_size) + 1

        # Get raw data
        with progressbar.ProgressBar(max_value=nr_batches, redirect_stdout=True) as bar:
            for i in range(nr_batches):
                logging.info(f"Extracting historical data. Starting from {start_date}")

                old_data = data

                batch_data, new_entries = self._etl_pipeline(
                    ExchangeData,
                    self.base_candle_size,
                    update_duplicate=False,
                    start_date=start_date,
                    header=header
                )

                data = pd.concat([data, batch_data], axis=0).drop_duplicates(["open_time"])

                start_date = get_end_date(start_date, self.base_candle_size, self.batch_size)

                bar.update(i)

                if old_data.equals(data):
                    break

        # Get structured data
        self._etl_pipeline(
            StructuredData,
            self.candle_size,
            use_db=True,
            remove_zeros=True,
            remove_rows=True,
            update_duplicate=False,
            start_date=self.start_date,
            header=header
        )

        start_pipeline = self.generate_new_signal(header)

        if start_pipeline:
            self._start_kline_websockets(self.symbol, self._websocket_callback, header=header)

        remove_pipeline_loading(cache, self.pipeline_id)

    def stop_data_ingestion(self, header='', raise_exception=False, force=False):
        """
        Public method which stops the data pipeline for the symbol.

        Returns
        -------
        None

        """
        logging.info(header + f"Stopping {', '.join(self.streams)} data stream(s).")

        self._stop_websocket()

        self.delete_last_entry()

        payload = {
            "pipeline_id": self.pipeline_id,
            "force": force
        }

        response = start_stop_symbol_trading(payload, 'stop')

        if response["success"]:
            Pipeline.objects.filter(id=self.pipeline_id).update(active=False, open_time=None)
            Position.objects.filter(pipeline__id=self.pipeline_id).update(position=0)
        else:
            logging.info(response["message"])

            if raise_exception:
                raise DataPipelineCouldNotBeStopped(response["message"])

        return response["success"]

    def _etl_pipeline(
        self,
        model_class,
        candle_size,
        reference_candle_size='5m',
        data=None,
        start_date=None,
        use_db=False,
        remove_zeros=False,
        remove_rows=False,
        columns_aggregation=const.COLUMNS_AGGREGATION,
        update_duplicate=False,
        header='',
    ):

        # Extract
        if data is None:
            if not use_db:
                data = extract_data(self.get_historical_klines, self.symbol, candle_size,
                                    start_date=start_date, klines_batch_size=self.batch_size)
            else:
                data = extract_data_db(ExchangeData, self.symbol, self.base_candle_size, start_date=start_date)

        # Transform
        transformed_data = transform_data(
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
        new_entries = load_data(
            model_class,
            transformed_data,
            pipeline_id=self.pipeline_id,
            update_duplicate=update_duplicate,
            header=header,
        )

        self.print_added_entries(new_entries, model_class)

        return data, new_entries

    def _start_kline_websockets(self, symbol, callback, header=''):

        streams = [
            f"{symbol.lower()}@kline_{self.base_candle_size}",
            f"{symbol.lower()}@kline_{self.candle_size}"
        ]

        logging.info(header + f"Starting {', '.join(streams)} data stream(s).")

        self.streams = streams

        self.conn_key = self.start_multiplex_socket(lambda row: callback(row, header), streams)

    def _stop_websocket(self):
        self.stop_socket(self.conn_key)

    # number of consecutive failed signal generations after which the
    # pipeline is stopped and its position closed
    MAX_CONSECUTIVE_FAILURES = 3

    def generate_new_signal(self, header):

        success, message = trigger_signal(self.pipeline_id, header=header)

        failures_key = f"signal_failures {self.pipeline_id}"

        if success:
            cache.delete(failures_key)
        else:
            # NOTE: a "Too many retries" polling timeout is deliberately
            # treated like any other failure below. Re-triggering a fresh
            # signal here would enqueue a duplicate job while the first one
            # may still be running.

            logging.warning(header + message)

            if "not active" in message:
                # the pipeline is gone from the DB - stop streaming right away
                stop_pipeline(self.pipeline_id, header, raise_exception=False)
                return success

            # a single failure can be transient (worker hiccup, queue
            # backlog): skip this candle and only liquidate the position
            # after several consecutive failures
            failures = cache.incr(failures_key)

            if failures >= self.MAX_CONSECUTIVE_FAILURES:
                logging.warning(
                    header + f"{failures} consecutive signal failures. Stopping pipeline."
                )
                cache.delete(failures_key)
                stop_pipeline(self.pipeline_id, header, raise_exception=False)
                send_alert(
                    title="Pipeline stopped after consecutive signal failures",
                    body=(
                        f"Pipeline {self.pipeline_id} ({self.symbol}): {failures} "
                        f"consecutive signal failures (last: {message}). The pipeline "
                        f"was stopped and its position closed."
                    ),
                    severity="critical",
                    dedup_key=f"signal-failures-stop-{self.pipeline_id}",
                )
                publish_pipeline_event(
                    EVENT_DEACTIVATED, self.pipeline_id,
                    reason=f"{failures} consecutive signal failures (last: {message})",
                )
            else:
                logging.info(
                    header + f"Skipping candle ({failures} consecutive signal failures)."
                )
                send_alert(
                    title="Signal generation failed - candle skipped",
                    body=(
                        f"Pipeline {self.pipeline_id} ({self.symbol}): {message} "
                        f"(failure {failures}/{self.MAX_CONSECUTIVE_FAILURES} - the "
                        f"pipeline stops when the threshold is reached)."
                    ),
                    severity="warning",
                    dedup_key=f"signal-failures-{self.pipeline_id}",
                )

        return success

    def _websocket_callback(self, row, header=''):

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

        data = pd.concat([data, new_data], axis=0)

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
        new_entries = False
        if len(data) != data_length:
            rows = data.iloc[data_length - 1:-1].reset_index()

            data_length = len(data)

            _, new_entries = self._etl_pipeline(
                model_class,
                candle_size,
                reference_candle_size=candle_size,
                data=rows,
                remove_zeros=remove_zeros,
                remove_rows=remove_rows,
                columns_aggregation=const.COLUMNS_AGGREGATION,
                update_duplicate=True,
            )

        return data, data_length, new_entries

    def get_start_date(self):
        if self.start_date is not None:
            minimum_lookback_date = self.start_date
        else:
            max_window = get_pipeline_max_window(self.pipeline_id, settings.default_min_rows)
            minimum_lookback_date = get_minimum_lookback_date(max_window, self.candle_size)

        self.start_date = minimum_lookback_date

        return get_earliest_missing_date(minimum_lookback_date, self.symbol)

    def delete_last_entry(self):
        # ExchangeData/StructuredData rows are shared by every pipeline on the
        # same (symbol, exchange, interval). Only the still-forming candle
        # (close_time in the future) is safe to delete; removing a completed
        # candle would desync another pipeline that already acted on it.
        now = datetime.now(tz=pytz.utc)

        for model_class, candle_size in [
            (ExchangeData, self.base_candle_size),
            (StructuredData, self.candle_size)
        ]:
            last = model_class.objects.filter(
                symbol=self.symbol,
                exchange_id=self.exchange,
                interval=candle_size
            ).order_by('open_time').last()

            if last is not None and last.close_time is not None and last.close_time > now:
                last.delete()

    def print_added_entries(self, new_entries, model_class):

        logging.info(
            self.header + f"Added {new_entries} new {'row' if new_entries == 1 else 'rows'} into {model_class}.")
