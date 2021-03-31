import numpy as np

from quant_model.strategies import SMACrossoverBase
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class SMACrossoverVectBacktester(SMACrossoverBase, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, SMA_S, SMA_L, trading_costs=0, symbol='BTCUSDT'):
        SMACrossoverBase.__init__(self, SMA_S, SMA_L)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)

        return data
