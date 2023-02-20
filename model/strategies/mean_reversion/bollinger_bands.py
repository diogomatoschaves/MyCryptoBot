from collections import OrderedDict

import numpy as np

from model.strategies._mixin import StrategyMixin


class BollingerBands(StrategyMixin):
    """ Bollinger Bands Strategy:

    This strategy follows the principle of mean reversion, ie. that
    the price will revert back to the mean if it deviates by a certain amount,
    essentially going long or short when the price crosses a
    certain low and high threshold respectively.

    Parameters:
    -----------
    ma : int
        Moving average window.
    sd : int
        Standard deviation window.
    data : pd.DataFrame, default None
        Data to use in the strategy.
    **kwargs
        Additional arguments to pass to the `StrategyMixin` superclass.

    Attributes:
    -----------
    params : OrderedDict
        Ordered dictionary containing the strategy's parameters:
        - `ma`: moving average window.
        - `sd`: standard deviation window.

    Methods:
    --------
    __repr__(self)
        Return a string representation of the class instance.
    _get_test_title(self)
        Return a string with the title for the test.
    update_data(self)
        Retrieves and prepares the data.
    _calculate_positions(self, data)
        Calculate the position for each row in the data.
    _get_position(self, symbol)
        Return the position for a given symbol (not implemented).
    get_signal(self, row=None)
        Return the position signal for a given row.

    """

    def __init__(self, ma: int, sd: int, data=None, **kwargs):

        self._ma = ma
        self._sd = sd

        StrategyMixin.__init__(self, data, **kwargs)

        self.params = OrderedDict(
            ma=lambda x: int(x),
            sd=lambda x: float(x),
        )

    def __repr__(self):
        return "{}(symbol = {}, ma = {}, sd = {})".format(self.__class__.__name__, self.symbol, self._ma, self._sd)

    def _get_test_title(self):
        return "Testing Bollinger Bands Strategy: {} | ma = {} & sd = {}".format(self.symbol, self._ma, self._sd)

    def update_data(self):
        """ Retrieves and prepares the data.
        """
        super(BollingerBands, self).update_data()

        data = self.data

        data["sma"] = data[self.price_col].rolling(self._ma).mean()
        data["upper"] = data["sma"] + data[self.price_col].rolling(self._ma).std() * self._sd
        data["lower"] = data["sma"] - data[self.price_col].rolling(self._ma).std() * self._sd

        self.data = self._calculate_positions(data)

    def _calculate_positions(self, data):
        data["distance"] = data[self.price_col] - data["sma"]
        data["position"] = np.where(data[self.price_col] > data["upper"], -1, np.nan)
        data["position"] = np.where(data[self.price_col] < data["lower"], 1, data["position"])
        data["position"] = np.where(data["distance"] * data["distance"].shift(1) < 0, 0, data["position"])
        data["position"] = data["position"].ffill().fillna(0)

        return data

    def _get_position(self, symbol):
        return None

    def get_signal(self, row=None):

        if row is None:
            row = self.data.iloc[-1]

        return int(row["position"])
