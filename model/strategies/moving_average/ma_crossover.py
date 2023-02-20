from collections import OrderedDict
from typing import Literal

import numpy as np
from ta.trend import ema_indicator, sma_indicator

from model.strategies._mixin import StrategyMixin


class MovingAverageCrossover(StrategyMixin):
    """
    A strategy that uses two simple or exponential moving averages as a trigger for going long or short, with no neutral
    position. When the shorter moving average goes above the longer moving average it goes long, and goes short when the
    reverse holds true.

    Parameters:
    -----------
    sma_s: int
        The window size for the short moving average.
    sma_l: int
        The window size for the long moving average.
    moving_av: Literal["sma", "ema"], default='sma'
        The type of moving average to use. Either 'sma' for simple moving average, or 'ema' for exponential moving average.

    Attributes:
    -----------
    params : OrderedDict
        A dictionary of the parameters used to initialize the strategy.

    Methods:
    --------
    update_data():
        Retrieves and prepares the data for the strategy.

    _calculate_positions(data):
        Calculates the position values for the given data.

    get_signal(row=None):
        Gets the trading signal for a given row of data. If row is not specified, uses the last row of data.

    """

    def __init__(
            self,
            sma_s: int,
            sma_l: int,
            moving_av: Literal["sma", "ema"] = 'sma',
            data=None,
            **kwargs
    ):
        """
        Constructs a new instance of the MovingAverageCrossover class.

        Parameters:
        -----------
        sma_s: int
            The window size for the short moving average.
        sma_l: int
            The window size for the long moving average.
        moving_av: Literal["sma", "ema"], default='sma'
            The type of moving average to use. Either 'sma' for simple moving average, or 'ema' for exponential moving average.
        data: pandas.DataFrame, default=None
            The data to use for the strategy. If not specified, the data will be retrieved from the data source.
        kwargs:
            Additional keyword arguments to be passed to the parent class constructor.

        """
        self._sma_s = sma_s
        self._sma_l = sma_l
        self._moving_av = moving_av

        self.params = OrderedDict(sma_s=lambda x: int(x), sma_l=lambda x: int(x), moving_av=lambda x: x)

        StrategyMixin.__init__(self, data, **kwargs)

    def __repr__(self):
        """
        Returns a string representation of the MovingAverageCrossover instance.

        Returns:
        --------
        str:
            A string representation of the MovingAverageCrossover instance.
        """
        return "{}(symbol = {}, SMA_S = {}, SMA_L = {})".format(self.__class__.__name__, self.symbol, self._sma_s, self._sma_l)

    def _get_test_title(self):
        """
        Returns the title for the backtest report.

        Returns:
        --------
        str:
            The title for the backtest report.
        """
        return "Testing SMA strategy | {} | SMA_S = {} & SMA_L = {}".format(self.symbol, self._sma_s, self._sma_l)

    def update_data(self):
        """
        Retrieves and prepares the data for the strategy.
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
        """
        Calculates the position values for the given data.

        Parameters:
        -----------
        data: pandas.DataFrame
            The data to use for the calculation.

        Returns:
        --------
        pandas.DataFrame:
            The input DataFrame with an additional 'position' column containing the calculated position values.
        """
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)

        return data

    def get_signal(self, row=None):
        """
        Gets the trading signal for a given row of data.

        Parameters:
        -----------
        row: pandas.Series, default=None
            The row of data for which to get the trading signal. If not specified, the last row of data will be used.

        Returns:
        --------
        int:
            1 if the short moving average is above the long moving average, -1 if the short moving average is below the
            long moving average.
        """
        if row is None:
            row = self.data.iloc[-1]

        if row["SMA_S"] > row["SMA_L"]:
            return 1
        elif row["SMA_S"] < row["SMA_L"]:
            return -1
