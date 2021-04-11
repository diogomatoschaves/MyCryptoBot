import logging
import time

from data.binance import BinanceDataHandler
from shared.utils.logger import configure_logger

configure_logger()


def start_data_collection(base, quote, candle_size):

    binance_handler = BinanceDataHandler(base, quote, candle_size)

    binance_handler.start_data_ingestion()

    while True:
        time.sleep(10)
