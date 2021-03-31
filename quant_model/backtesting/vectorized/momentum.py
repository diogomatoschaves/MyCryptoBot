import numpy as np

from quant_model.strategies import MomentumBase
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class MomentumVectBacktester(MomentumBase, VectorizedBacktester):
    """ Class for the vectorized backtesting of simple Contrarian trading strategies.
    """

    def __init__(self, data, window=10, trading_costs=0, symbol='BTCUSDT'):
        MomentumBase.__init__(self, window)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):
        data["position"] = np.sign(data[self.returns_col].rolling(self.window, min_periods=1).mean())

        return data
