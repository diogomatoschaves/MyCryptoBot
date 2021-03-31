import numpy as np


class Momentum:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, window, returns_col='returns'):
        self.data = None
        self.window = window
        self.symbol = None
        self.returns_col = returns_col

    def __repr__(self):
        return "{}(symbol = {}, window = {})".format(self.__class__.__name__, self.symbol, self.window)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """
        data["rolling_returns"] = data[self.returns_col].rolling(self.window, min_periods=1).mean()
        return data

    def _set_parameters(self, window):
        """ Updates SMA parameters and resp. time series.
        """
        if window is not None:
            self.window = int(window)

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):
        data["position"] = np.sign(data[self.returns_col].rolling(self.window, min_periods=1).mean())

        return data

    def get_signal(self, row):
        if row["rolling_returns"] >= 0:
            return 1
        else:
            return -1
