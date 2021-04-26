import numpy as np

from model.strategies._mixin import StrategyMixin


class BollingerBands(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, ma, sd, data=None, **kwargs):

        self._ma = ma
        self._sd = sd

        StrategyMixin.__init__(self, data, **kwargs)

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

        self.data = data

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

        position = self._get_position(self.symbol)

        if position == 0: # when neutral
            if row[self.price_col] < row["lower"]:  # signal to go long
                return 1
            elif row[self.price_col] > row["upper"]:  # signal to go Short
                return -1
        elif position == 1:  # when long
            if row[self.price_col] > row["sma"]:
                if row[self.price_col] > row["upper"]:  # signal to go short
                    return -1
                else:
                    return 0
        elif position == -1: # when short
            if row[self.price_col] < row["sma"]:
                if row[self.price_col] < row["lower"]:  # signal to go long
                    return 1
                else:
                    return 0
