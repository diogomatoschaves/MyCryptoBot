import numpy as np

from quant_model.strategies import Momentum
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class MomentumVectBacktester(Momentum, VectorizedBacktester):
    """ Class for the vectorized backtesting of simple Contrarian trading strategies.
    """

    def __init__(self, data, window=10, trading_costs=0, symbol='BTCUSDT'):
        Momentum.__init__(self, window)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)
