from collections import OrderedDict
from typing import Literal

import numpy as np
from ta.trend import sma_indicator, ema_indicator

from model.strategies._mixin import StrategyMixin


class MovingAverage(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, ma: int, moving_av: Literal["sma", "ema"] = 'sma', data=None, **kwargs):

        self._ma = ma
        self._moving_av = moving_av

        self.params = OrderedDict(ma=lambda x: int(x))

        StrategyMixin.__init__(self, data, **kwargs)

    def __repr__(self):
        return "{}(symbol = {}, SMA = {})".format(self.__class__.__name__, self.symbol, self._ma)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | SMA_S = {}".format(self.symbol, self._ma)

    def update_data(self):
        """ Retrieves and prepares the data.
        """
        super(MovingAverage, self).update_data()

        if self._moving_av == 'sma':
            self.data["SMA"] = sma_indicator(close=self.data[self.price_col], window=self._ma)
        elif self._moving_av == 'ema':
            self.data["SMA"] = ema_indicator(close=self.data[self.price_col], window=self._ma)
        else:
            raise('Method not supported')

    def _calculate_positions(self, data):

        data["position"] = np.where(data["SMA"] > data[self.price_col], 1, -1)

        return data

    def get_signal(self, row=None):

        if row is None:
            row = self.data.iloc[-1]

        if row["SMA"] > row[self.price_col]:
            return 1
        elif row["SMA"] < row[self.price_col]:
            return -1

        elif row["SMA"] == row[self.price_col]:
            return 0
