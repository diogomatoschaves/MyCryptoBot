import numpy as np


class StrategyMixin:

    def __init__(self, data, price_col='close', returns_col='returns'):

        self.price_col = price_col
        self.returns_col = returns_col
        self.symbol = None

        if data is not None:
            self.data = data.copy()
            self.update_data()

    def _get_data(self):
        return self.data

    def set_data(self, data):
        if data is not None:
            self.data = data
            self.data = self.update_data()

    def set_parameters(self, params=None):
        """ Updates SMA parameters and resp. time series.
        """

        if params is None:
            return

        for param, new_value in params.items():
            setattr(self, f"_{param}", self.params[param](new_value))

        self.update_data()

    def _calculate_returns(self):

        data = self.data

        data[self.returns_col] = np.log(data[self.price_col] / data[self.price_col].shift(1))

        self.data = data

    def update_data(self):
        self._calculate_returns()
