import numpy as np
from ta.trend import sma_indicator, ema_indicator

from quant_model.strategies._mixin import StrategyMixin


class MA(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, sma, data=None, moving_av='sma', **kwargs):

        StrategyMixin.__init__(self, data, **kwargs)

        self.sma = sma
        self.mav = moving_av

    def __repr__(self):
        return "{}(symbol = {}, SMA = {})".format(self.__class__.__name__, self.symbol, self.sma)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | SMA_S = {}".format(self.symbol, self.sma)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """
        data = super(MA, self).update_data(data)

        if self.mav == 'sma':
            data["SMA"] = sma_indicator(close=data[self.price_col], window=self.sma)
        elif self.mav == 'ema':
            data["SMA"] = ema_indicator(close=data[self.price_col], window=self.sma)
        else:
            raise('Method not supported')

        return data

    def set_parameters(self, sma=None):
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
