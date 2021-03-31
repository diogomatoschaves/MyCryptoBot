import numpy as np

from quant_model.strategies import SMABase
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class SMAVectBacktester(SMABase, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, sma, trading_costs=0, symbol='BTCUSDT'):
        SMABase.__init__(self, sma)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):

        data["position"] = np.where(data["SMA"] > data[self.price_col], 1, -1)

        return data
