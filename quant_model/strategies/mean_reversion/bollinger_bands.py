import numpy as np

from quant_model.strategies._mixin import StrategyMixin


class BollingerBands(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, ma, sd, data=None, **kwargs):

        self.ma = ma
        self.sd = sd

        StrategyMixin.__init__(self, data, **kwargs)

    def __repr__(self):
        return "{}(symbol = {}, ma = {}, sd = {})".format(self.__class__.__name__, self.symbol, self.ma, self.sd)

    def _get_test_title(self):
        return "Testing Bollinger Bands Strategy: {} | ma = {} & sd = {}".format(self.symbol, self.ma, self.sd)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """
        data = super(BollingerBands, self).update_data(data)

        data["sma"] = data[self.price_col].rolling(self.ma).mean()
        data["upper"] = data["sma"] + data[self.price_col].rolling(self.ma).std() * self.sd
        data["lower"] = data["sma"] - data[self.price_col].rolling(self.ma).std() * self.sd

        return data

    def set_parameters(self, params=None):
        """ Updates SMA parameters and resp. time series.
        """

        if params is None:
            return

        if not isinstance(params, (tuple, list, type(np.array([])))):
            print(f"Invalid Parameters {params}")
            return

        ma, sd = params

        if ma is not None:
            self.ma = int(ma)
        if sd is not None:
            self.sd = sd

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):
        data["distance"] = data[self.price_col] - data["sma"]
        data["position"] = np.where(data[self.price_col] > data["upper"], -1, np.nan)
        data["position"] = np.where(data[self.price_col] < data["lower"], 1, data["position"])
        data["position"] = np.where(data["distance"] * data["distance"].shift(1) < 0, 0, data["position"])
        data["position"] = data["position"].ffill().fillna(0)

        return data

    def get_signal(self, row):
        if self.position == 0: # when neutral
            if row[self.price_col] < row["lower"]:  # signal to go long
                return 1
            elif row[self.price_col] > row["upper"]:  # signal to go Short
                return -1
        elif self.position == 1:  # when long
            if row[self.price_col] > row["sma"]:
                if row[self.price_col] > row["upper"]:  # signal to go short
                    return 1
                else:
                    return 0
        elif self.position == -1: # when short
            if row[self.price_col] < row["sma"]:
                if row[self.price_col] < row["lower"]:  # signal to go long
                    return 1
                else:
                    return 0
