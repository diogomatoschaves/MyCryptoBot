import numpy as np

from strategies.backtesting.strategies import SMABase
from strategies.backtesting.vectorized.base import VectorizedBacktester


class SMAVectBacktester(SMABase, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, SMA_S, SMA_L, trading_costs=0, symbol='BTCUSDT'):
        SMABase.__init__(self)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.SMA_S = SMA_S
        self.SMA_L = SMA_L

        self._update_data()

    def test_strategy(self, sma=None, plot_results=True):
        """ Backtests the trading strategy.
        """

        self._set_parameters(sma)

        data = self.data.dropna().copy()
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)

        title = self.__repr__()

        return self._assess_strategy(data, title, plot_results)
