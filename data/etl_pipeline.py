from data.binance import BinanceDataHandler


def start_data_collection(base, quote, candle_size='1h'):

    binance_handler = BinanceDataHandler(base, quote, candle_size)

    binance_handler.start_data_ingestion()
