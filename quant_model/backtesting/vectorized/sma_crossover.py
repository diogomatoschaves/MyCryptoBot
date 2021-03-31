import numpy as np

from quant_model.strategies import MACrossover
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class MACrossoverVectBacktester(MACrossover, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, SMA_S, SMA_L, trading_costs=0, symbol='BTCUSDT', moving_av='sma', **kwargs):
        MACrossover.__init__(self, SMA_S, SMA_L, moving_av, **kwargs)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)
