import numpy as np

from quant_model.strategies import MA
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class MAVectBacktester(MA, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, sma, trading_costs=0, symbol='BTCUSDT', moving_av='sma', **kwargs):
        MA.__init__(self, sma, moving_av, **kwargs)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)
