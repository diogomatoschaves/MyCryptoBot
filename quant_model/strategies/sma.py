import numpy as np
from ta.trend import sma_indicator, ema_indicator

from quant_model.strategies.mixin import StrategyMixin


class MA(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, sma, moving_av='sma', **kwargs):
        self.data = data.copy()
        self.sma = sma
        self.symbol = None
        self.price_col = 'close'
        self.mav = moving_av

        self.data = self.update_data(self.data)

    def __repr__(self):
        return "{}(symbol = {}, SMA = {})".format(self.__class__.__name__, self.symbol, self.sma)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | SMA_S = {}".format(self.symbol, self.sma)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """
        self._calculate_returns()

        if self.mav == 'sma':
            data["SMA"] = sma_indicator(close=data[self.price_col], window=self.sma)
        elif self.mav == 'ema':
            data["SMA"] = ema_indicator(close=data[self.price_col], window=self.sma)
        else:
            raise('Method not supported')

        return data

    def _set_parameters(self, sma=None):
        """ Updates SMA parameters and resp. time series.
        """

        if sma is None:
            return

        if not isinstance(sma, (int, float)):
            print(f"Invalid Parameters {sma}")
            return

        self.sma = int(sma)

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):

        data["position"] = np.where(data["SMA"] > data[self.price_col], 1, -1)

        return data

    def get_signal(self, row):
        if row["SMA"] > row[self.price_col]:
            return 1
        elif row["SMA"] < row[self.price_col]:
            return -1
