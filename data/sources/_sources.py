from data.sources.binance import BinanceDataHandler


class DataHandler:

    def __init__(self, pipeline, header=''):

        self.binance_handler = BinanceDataHandler(pipeline.symbol.name, pipeline.interval, pipeline.id)

        self.binance_handler.start_data_ingestion(header=header)
