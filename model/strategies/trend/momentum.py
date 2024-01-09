import numpy as np

from model.strategies._mixin import StrategyMixin
from collections import OrderedDict


class Momentum(StrategyMixin):
    """
    this Momentum strategy calculates the rolling average return over a specified window of time,
    and generates trading signals based on the sign of this rolling average. When the rolling average
    return is positive, the strategy generates a long signal (i.e., buy), and when it is negative,
    it generates a short signal (i.e., sell). The strategy takes a neutral side when the rolling average is zero.

    Parameters
    ----------
    window : int
        Rolling window for computing the momentum.
    data : pd.DataFrame
        Input data, with at least a 'returns_col' column.
    **kwargs
        Additional keyword arguments.

    Attributes
    ----------
    _window : int
        Rolling window for computing the momentum.
    params : OrderedDict
        Dictionary of hyperparameters for the strategy.

    Methods
    -------
    update_data()
        Retrieves and prepares the data.
    calculate_positions(data)
        Calculates the positions of the strategy.
    get_signal(row=None)
        Returns the trading signal for a given row of data.

    """

    def __init__(self, window: int, data=None, **kwargs):

        self._window = window

        StrategyMixin.__init__(self, data, **kwargs)

        self.params = OrderedDict(window=lambda x: int(x))

    def __repr__(self):
        """
        Return a string representation of the class.
        """
        return "{}(symbol = {}, window = {})".format(self.__class__.__name__, self.symbol, self._window)

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
        data = super().update_data(data)

        data["rolling_returns"] = data[self.returns_col].rolling(self._window, min_periods=1).mean()

        return data

    def calculate_positions(self, data):
        """
        Calculates the positions of the strategy.

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe with the input data.

        Returns
        -------
        pd.DataFrame
            Dataframe with the positions of the strategy.
        """
        data["side"] = np.sign(data["rolling_returns"])

        return data

    def get_signal(self, row=None):
        """
        Returns the trading signal for a given row of data.

        Parameters
        ----------
        row : pd.Series, optional
            Row of data to calculate the signal for. If None, the last row of the data is used.

        Returns
        -------
        int
            The trading signal (-1 for sell, 1 for buy, 0 for hold).
        """
        if row is None:
            row = self.data.iloc[-1]

        if row["rolling_returns"] > 0:
            return 1
        elif row["rolling_returns"] < 0:
            return -1
        else:
            return 0
