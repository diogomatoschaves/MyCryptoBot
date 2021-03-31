import numpy as np
import btalib as ta
from ta.trend import ema_indicator, sma_indicator


class MACrossover:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, SMA_S, SMA_L, moving_av='sma', **kwargs):
        self.data = None
        self.SMA_S = SMA_S
        self.SMA_L = SMA_L
        self.symbol = None
        self.mav = moving_av
        self.price_col = 'close'

    def __repr__(self):
        return "{}(symbol = {}, SMA_S = {}, SMA_L = {})".format(self.__class__.__name__, self.symbol, self.SMA_S, self.SMA_L)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """

        if self.mav == 'sma':
            data["SMA_S"] = sma_indicator(close=data[self.price_col], window=self.SMA_S)
            data["SMA_L"] = sma_indicator(close=data[self.price_col], window=self.SMA_L)

        elif self.mav == 'ema':
            data["SMA_S"] = ema_indicator(close=data[self.price_col], window=self.SMA_S)
            data["SMA_L"] = ema_indicator(close=data[self.price_col], window=self.SMA_L)
        else:
            raise('Method not supported')

        return data

    def _set_parameters(self, sma=None):
        """ Updates SMA parameters and resp. time series.
        """

        if sma is None:
            return

        if not isinstance(sma, (tuple, list, type(np.array([])))):
            print(f"Invalid Parameters {sma}")
            return

        SMA_S, SMA_L = sma

        if SMA_S is not None:
            self.SMA_S = int(SMA_S)
        if SMA_L is not None:
            self.SMA_L = int(SMA_L)

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)

        return data

    def get_signal(self, row):
        if row["SMA_S"] > row["SMA_L"]:
            return 1
        elif row["SMA_S"] < row["SMA_L"]:
            return -1
