class DataHandler:
    def __init__(self, pipeline, header=''):
        from data.sources.binance import BinanceDataHandler

        self.binance_handler = BinanceDataHandler(pipeline.symbol.name, pipeline.interval, pipeline.id)
