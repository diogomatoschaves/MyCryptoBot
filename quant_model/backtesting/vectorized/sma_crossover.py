import numpy as np

from quant_model.strategies import SMACrossoverBase
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class SMAVectBacktester(SMACrossoverBase, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, SMA_S, SMA_L, trading_costs=0, symbol='BTCUSDT'):
        SMACrossoverBase.__init__(self, SMA_S, SMA_L)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def test_strategy(self, sma=None, plot_results=True):
        """ Backtests the trading strategy.
        """

        self._set_parameters(sma)

        data = self.data.dropna().copy()
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)

        title = self.__repr__()

        return self._assess_strategy(data, title, plot_results)
