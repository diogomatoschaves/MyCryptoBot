import numpy as np

from quant_model.strategies import MeanRev
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class MeanRevVectBacktester(MeanRev, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.

    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    ma: int
        time window in days for shorter SMA
    sd: int
        time window in days for longer SMA

    """

    def __init__(self, data, ma, sd, trading_costs=0, symbol='BTCUSDT'):
        MeanRev.__init__(self, ma, sd)
        VectorizedBacktester.__init__(self, data, trading_costs=trading_costs, symbol=symbol)

        self.data = self.update_data(self.data)
