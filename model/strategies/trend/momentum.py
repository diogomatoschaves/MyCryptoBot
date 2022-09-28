import numpy as np

from model.strategies._mixin import StrategyMixin
from collections import OrderedDict


class Momentum(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, window: int, data=None, **kwargs):

        self._window = window

        StrategyMixin.__init__(self, data, **kwargs)

        self.params = OrderedDict(window=lambda x: int(x))

    def __repr__(self):
        return "{}(symbol = {}, window = {})".format(self.__class__.__name__, self.symbol, self._window)

    def _get_test_title(self):
        return "Testing Momentum strategy | {} | window: {}".format(self.symbol, self._window)

    def update_data(self):
        """ Retrieves and prepares the data.
        """
        super(Momentum, self).update_data()

        self.data["rolling_returns"] = self.data[self.returns_col].rolling(self._window, min_periods=1).mean()

    def _calculate_positions(self, data):
        data["position"] = np.sign(data[self.returns_col].rolling(self._window, min_periods=1).mean())

        return data

    def get_signal(self, row=None):

        if row is None:
            row = self.data.iloc[-1]

        if row["rolling_returns"] > 0:
            return 1
        elif row["rolling_returns"] < 0:
            return -1
        else:
            return 0
