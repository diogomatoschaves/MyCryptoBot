import numpy as np


class SMABase:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, SMA_S, SMA_L):
        self.data = None
        self.SMA_S = SMA_S
        self.SMA_L = SMA_L
        self.symbol = None

    def __repr__(self):
        return "{}(symbol = {}, SMA_S = {}, SMA_L = {})".format(self.__class__.__name__, self.symbol, self.SMA_S, self.SMA_L)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """

        data["SMA_S"] = data["close"].rolling(self.SMA_S).mean()
        data["SMA_L"] = data["close"].rolling(self.SMA_L).mean()

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
