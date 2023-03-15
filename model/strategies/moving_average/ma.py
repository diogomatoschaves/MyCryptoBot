from collections import OrderedDict
from typing import Literal

import numpy as np
from ta.trend import sma_indicator, ema_indicator

from model.strategies._mixin import StrategyMixin


class MovingAverage(StrategyMixin):
    """
    Strategy that uses a simple or exponential moving average as a trigger for
    going long or short, with no neutral position. When the price crosses over
    above the moving average it goes long, and vice versa when the price crosses below.

    Parameters
    ----------
    ma : int
        Moving average window.
    moving_av : Literal["sma", "ema"], optional
        Type of moving average (simple or exponential), by default 'sma'.
    data : pd.DataFrame, optional
        Dataframe of OHLCV data, by default None.
    **kwargs : dict, optional
        Additional keyword arguments to be passed to parent class, by default None.

    Attributes
    ----------
    params : OrderedDict
        Parameters for the strategy, by default {"ma": lambda x: int(x)}

    Methods
    -------
    update_data()
        Retrieves and prepares the data.
    _calculate_positions(data)
        Calculates positions based on strategy rules.
    get_signal(row)
        Returns signal based on current data.

    """
    def __init__(self, ma: int, moving_av: Literal["sma", "ema"] = 'sma', data=None, **kwargs):
        """
        Parameters
        ----------
        ma : int
            Moving average window.
        moving_av : Literal["sma", "ema"], optional
            Type of moving average (simple or exponential), by default 'sma'.
        data : pd.DataFrame, optional
            Dataframe of OHLCV data, by default None.
        **kwargs : dict, optional
            Additional keyword arguments to be passed to parent class, by default None.
        """
        self._ma = ma
        self._moving_av = moving_av

        self.params = OrderedDict(ma=lambda x: int(x))

        StrategyMixin.__init__(self, data, **kwargs)

    def __repr__(self):
        return "{}(symbol = {}, SMA = {})".format(self.__class__.__name__, self.symbol, self._ma)

    def update_data(self, data):
        """
        Updates the input data with additional columns required for the strategy.

        Parameters
        ----------
        data : pd.DataFrame
            OHLCV data to be updated.

        Returns
        -------
        pd.DataFrame
            Updated OHLCV data containing additional columns.
        """
        super().update_data(data)

        if self._moving_av == 'sma':
            data["SMA"] = sma_indicator(close=data[self.price_col], window=self._ma)
        elif self._moving_av == 'ema':
            data["SMA"] = ema_indicator(close=data[self.price_col], window=self._ma)
        else:
            raise('Method not supported')

        return data

    def _calculate_positions(self, data):
        """
        Calculates positions based on strategy rules.

        Parameters
        ----------
        data : pd.DataFrame
            OHLCV data.

        Returns
        -------
        pd.DataFrame
            OHLCV data with additional 'position' column containing -1 for short, 1 for long.
        """
        data["position"] = np.where(data["SMA"] > data[self.price_col], 1, 0)
        data["position"] = np.where(data["SMA"] < data[self.price_col], -1, data["position"])
        return data

    def get_signal(self, row=None):
        """
        Returns signal based on current data.

        Parameters
        ----------
        row : pd.Series, optional
            Row of OHLCV data to generate signal for, by default None.

        Returns
        -------
        int
            Signal (-1 for short, 1 for long, 0 for neutral).
        """
        if row is None:
            row = self.data.iloc[-1]

        if row["SMA"] > row[self.price_col]:
            return 1
        elif row["SMA"] < row[self.price_col]:
            return -1

        elif row["SMA"] == row[self.price_col]:
            return 0
