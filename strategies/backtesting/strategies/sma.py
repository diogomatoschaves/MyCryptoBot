

class SMABase:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self):
        self.data = None
        self.SMA_S = None
        self.SMA_L = None
        self.symbol = None

    def __repr__(self):
        return "{}(symbol = {}, SMA_S = {}, SMA_L = {})".format(self.__class__.__name__, self.symbol, self.SMA_S, self.SMA_L)

    def _update_data(self):
        """ Retrieves and prepares the data.
        """

        self.data["SMA_S"] = self.data["close"].rolling(self.SMA_S).mean()
        self.data["SMA_L"] = self.data["close"].rolling(self.SMA_L).mean()

    def _set_parameters(self, SMA_S = None, SMA_L = None):
        """ Updates SMA parameters and resp. time series.
        """
        if SMA_S is not None:
            self.SMA_S = int(SMA_S)
            self.data["SMA_S"] = self.data["close"].rolling(self.SMA_S).mean()
        if SMA_L is not None:
            self.SMA_L = int(SMA_L)
            self.data["SMA_L"] = self.data["close"].rolling(self.SMA_L).mean()
