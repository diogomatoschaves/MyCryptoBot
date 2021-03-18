

class MeanRevBase:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self):
        self.data = None
        self.price_col = None
        self.symbol = None

    def __repr__(self):
        return "{}(symbol = {}, ma = {}, sd = {})".format(self.__class__.__name__, self.symbol, self.ma, self.sd)

    def _update_data(self):
        """ Retrieves and prepares the data.
        """

        sma = self.data[self.price_col].rolling(self.ma).mean()
        self.data["upper"] = sma + self.data[self.price_col].rolling(self.ma).std() * self.sd
        self.data["lower"] = sma - self.data[self.price_col].rolling(self.ma).std() * self.sd

    def _set_parameters(self, ma = None, sd = None):
        """ Updates SMA parameters and resp. time series.
        """
        if ma is not None:
            self.ma = int(ma)
        if sd is not None:
            self.sd = sd

        self._update_data()
