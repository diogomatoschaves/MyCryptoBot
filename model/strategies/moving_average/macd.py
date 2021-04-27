from collections import OrderedDict

import numpy as np
import pandas as pd
from ta.trend import MACD

from model.strategies._mixin import StrategyMixin


class MovingAverageConvergenceDivergence(MACD, StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, window_slow=26, window_fast=12, window_signal=9, data=None, **kwargs):

        MACD.__init__(self, pd.Series(), window_slow, window_fast, window_signal)
        StrategyMixin.__init__(self, data, **kwargs)

        self._close = pd.Series()

        self.params = OrderedDict(
            window_slow=lambda x: int(x),
            window_fast=lambda x: int(x),
            window_signal=lambda x: int(x)
        )

    def __repr__(self):
        return "{}(symbol = {}, fast = {}, slow = {}, signal = {})".format(
            self.__class__.__name__, self.symbol, self._window_fast, self._window_slow, self._window_sign
        )

    def _get_test_title(self):
        return "Testing MACD strategy | {} | fast = {}, slow = {}, signal = {}".format(
            self.symbol, self._window_fast, self._window_slow, self._window_sign
        )

    def update_data(self):
        """ Retrieves and prepares the data.
        """

        super(MovingAverageConvergenceDivergence, self).update_data()

        self._close = self.data[self.price_col]
        self._run()

        self.data["macd_diff"] = self.macd_diff()

    def _calculate_positions(self, data):
        data["position"] = np.where(data["macd_diff"] > 0, 1, -1)

        return data

    def get_signal(self, row=None):

        if row is None:
            row = self.data.iloc[-1]

        if row["macd_diff"] > 0:
            return 1
        elif row["macd_diff"] < 0:
            return -1
