from collections import OrderedDict

import numpy as np
import pandas as pd
from ta.trend import MACD

from model.strategies._mixin import StrategyMixin


class MovingAverageConvergenceDivergence(MACD, StrategyMixin):
    """
    Strategy that uses 3 different parameters to calculate the side.
    It calculates the difference between the slow and the fast exponential moving averages,
    and compares that with the signal window to get the signal. When the signal moving average goes
    above the difference of the fast and slow, it goes long, and goes short when the reverse holds true.

    Parameters
    ----------
    window_slow : int, optional
        Slow moving average window, by default 26
    window_fast : int, optional
        Fast moving average window, by default 12
    window_sign : int, optional
        Signal moving average window, by default 9
    data : pd.DataFrame, optional
        Data to use, by default None
    **kwargs
        Keyword arguments to pass to parent class

    Attributes
    ----------
    params : collections.OrderedDict
        Parameters of the strategy
    _close : pd.Series
        Close prices of the data
    """

    def __init__(
        self,
        window_slow: int = 26,
        window_fast: int = 12,
        window_sign: int = 9,
        data: pd.DataFrame = None,
        **kwargs
    ):
        """
        Constructs all the necessary attributes for the MACD strategy object.

        Parameters
        ----------
        window_slow : int, optional
            Slow moving average window, by default 26
        window_fast : int, optional
            Fast moving average window, by default 12
        window_signal : int, optional
            Signal moving average window, by default 9
        data : pd.DataFrame, optional
            Data to use, by default None
        **kwargs
            Keyword arguments to pass to parent class
        """
        MACD.__init__(self, pd.Series(dtype='float64'), window_slow, window_fast, window_sign)
        StrategyMixin.__init__(self, data, **kwargs)

        self._close = pd.Series(dtype='float64')

        self.params = OrderedDict(
            window_slow=lambda x: int(x),
            window_fast=lambda x: int(x),
            window_sign=lambda x: int(x)
        )

    def __repr__(self) -> str:
        """
        Returns the string representation of the object.

        Returns
        -------
        str
            String representation of the object.
        """
        return "{}(symbol = {}, fast = {}, slow = {}, signal = {})".format(
            self.__class__.__name__, self.symbol, self._window_fast, self._window_slow, self._window_sign
        )

    def update_data(self, data) -> None:
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

        self._close = data[self.price_col]
        self._run()

        data["macd_diff"] = self.macd_diff()

        return data

    def _calculate_positions(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates positions based on MACD difference.

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe containing MACD difference column

        Returns
        -------
        pd.DataFrame
            Dataframe containing position column.
        """
        data["position"] = np.where(data["macd_diff"] > 0, 1, -1)

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

        if row["macd_diff"] > 0:
            return 1
        elif row["macd_diff"] < 0:
            return -1
