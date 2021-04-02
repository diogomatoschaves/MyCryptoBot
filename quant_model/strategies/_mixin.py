import numpy as np


class StrategyMixin:

    def __init__(self, data, price_col='close', returns_col='returns'):

        self.price_col = price_col
        self.returns_col = returns_col
        self.symbol = None

        if data is not None:
            self.data = self.update_data(data.copy())

    def _get_data(self):
        return self.data

    def set_data(self, data):
        if data is not None:
            self.data = data
            self.data = self.update_data(self.data)

    def _calculate_returns(self, data):
        data[self.returns_col] = np.log(data[self.price_col] / data[self.price_col].shift(1))

        return data

    def update_data(self, data):
        return self._calculate_returns(data)
