from collections import OrderedDict
from typing import Literal

import numpy as np
from ta.trend import ema_indicator, sma_indicator

from model.strategies._mixin import StrategyMixin


class MovingAverageCrossover(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(
        self,
        sma_s: int,
        sma_l: int,
        moving_av: Literal["sma", "ema"] = 'sma',
        data=None, **kwargs
    ):

        self._sma_s = sma_s
        self._sma_l = sma_l
        self._moving_av = moving_av

        self.params = ["sma_s", "sma_l"]
        self.params = OrderedDict(sma_s=lambda x: int(x), sma_l=lambda x: int(x), moving_av=lambda x: x)

        StrategyMixin.__init__(self, data, **kwargs)

    def __repr__(self):
        return "{}(symbol = {}, SMA_S = {}, SMA_L = {})".format(self.__class__.__name__, self.symbol, self._sma_s, self._sma_l)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | SMA_S = {} & SMA_L = {}".format(self.symbol, self._sma_s, self._sma_l)

    def update_data(self):
        """ Retrieves and prepares the data.
        """
        super(MovingAverageCrossover, self).update_data()

        data = self.data

        if self._moving_av == 'sma':
            data["SMA_S"] = sma_indicator(close=data[self.price_col], window=self._sma_s)
            data["SMA_L"] = sma_indicator(close=data[self.price_col], window=self._sma_l)

        elif self._moving_av == 'ema':
            data["SMA_S"] = ema_indicator(close=data[self.price_col], window=self._sma_s)
            data["SMA_L"] = ema_indicator(close=data[self.price_col], window=self._sma_l)
        else:
            raise ('Method not supported')

        self.data = data

    def _calculate_positions(self, data):
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)

        return data

    def get_signal(self, row=None):

        if row is None:
            row = self.data.iloc[-1]

        if row["SMA_S"] > row["SMA_L"]:
            return 1
        elif row["SMA_S"] < row["SMA_L"]:
            return -1
