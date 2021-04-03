import numpy as np

from quant_model.strategies._mixin import StrategyMixin


class Momentum(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, window, data, **kwargs):

        self.window = window

        StrategyMixin.__init__(self, data, **kwargs)

    def __repr__(self):
        return "{}(symbol = {}, window = {})".format(self.__class__.__name__, self.symbol, self.window)

    def _get_test_title(self):
        return "Testing Momentum strategy | {} | window: {}".format(self.symbol, self.window)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """
        data = super(Momentum, self).update_data(data)

        data["rolling_returns"] = data[self.returns_col].rolling(self.window, min_periods=1).mean()
        return data

    def set_parameters(self, window):
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
