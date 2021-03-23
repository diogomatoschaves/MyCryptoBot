import numpy as np

from strategies.backtesting.strategies import MomentumBase
from strategies.backtesting.vectorized.base import VectorizedBacktester


class MomentumVectBacktester(MomentumBase, VectorizedBacktester):
    """ Class for the vectorized backtesting of simple Contrarian trading strategies.
    """

    def __init__(self, data, window=10, trading_costs=0, symbol='BTCUSDT'):
        MomentumBase.__init__(self, window)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def test_strategy(self, window=None, plot_results=True):
        """ Backtests the trading strategy.
        """
        self._set_parameters(window)

        data = self.data.copy().dropna()
        data["position"] = np.sign(data[self.returns_col].rolling(self.window, min_periods=1).mean())

        title = self.__repr__()

        return self._assess_strategy(data, data, title, plot_results)
