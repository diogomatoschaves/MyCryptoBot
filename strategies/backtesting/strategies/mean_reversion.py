import numpy as np


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

        self.data["sma"] = self.data[self.price_col].rolling(self.ma).mean()
        self.data["upper"] = self.data["sma"] + self.data[self.price_col].rolling(self.ma).std() * self.sd
        self.data["lower"] = self.data["sma"] - self.data[self.price_col].rolling(self.ma).std() * self.sd

    def _set_parameters(self, ma_sd_pair=None):
        """ Updates SMA parameters and resp. time series.
        """

        if ma_sd_pair is None:
            return

        if not isinstance(ma_sd_pair, (tuple, list, type(np.array([])))):
            print(f"Invalid Parameters {ma_sd_pair}")
            return

        ma, sd = ma_sd_pair

        if ma is not None:
            self.ma = int(ma)
        if sd is not None:
            self.sd = sd

        self._update_data()
