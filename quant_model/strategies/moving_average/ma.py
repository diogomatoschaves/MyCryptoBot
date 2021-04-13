import numpy as np
from ta.trend import sma_indicator, ema_indicator

from quant_model.strategies._mixin import StrategyMixin


class MovingAverage(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, sma, moving_av='sma', data=None, **kwargs):

        self.sma = sma
        self.mav = moving_av

        StrategyMixin.__init__(self, data, **kwargs)

    def __repr__(self):
        return "{}(symbol = {}, SMA = {})".format(self.__class__.__name__, self.symbol, self.sma)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | SMA_S = {}".format(self.symbol, self.sma)

    def update_data(self):
        """ Retrieves and prepares the data.
        """
        super(MovingAverage, self).update_data()

        if self.mav == 'sma':
            self.data["SMA"] = sma_indicator(close=self.data[self.price_col], window=self.sma)
        elif self.mav == 'ema':
            self.data["SMA"] = ema_indicator(close=self.data[self.price_col], window=self.sma)
        else:
            raise('Method not supported')

    def set_parameters(self, sma=None):
        """ Updates SMA parameters and resp. time series.
        """

        if sma is None:
            return

        if not isinstance(sma, (int, float)):
            print(f"Invalid Parameters {sma}")
            return

        self.sma = int(sma)

        self.update_data()

    def _calculate_positions(self, data):

        data["position"] = np.where(data["SMA"] > data[self.price_col], 1, -1)

        return data

    def get_signal(self, row=None):

        if row is None:
            row = self.data.iloc[-1]

        if row["SMA"] > row[self.price_col]:
            return 1
        elif row["SMA"] < row[self.price_col]:
            return -1
