import numpy as np


class MeanRevBase:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, ma, sd):
        self.data = None
        self.price_col = 'close'
        self.ma = ma
        self.sd = sd
        self.symbol = None

    def __repr__(self):
        return "{}(symbol = {}, ma = {}, sd = {})".format(self.__class__.__name__, self.symbol, self.ma, self.sd)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """

        data["sma"] = data[self.price_col].rolling(self.ma).mean()
        data["upper"] = data["sma"] + data[self.price_col].rolling(self.ma).std() * self.sd
        data["lower"] = data["sma"] - data[self.price_col].rolling(self.ma).std() * self.sd

        return data

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

        self.data = self.update_data(self.data)

    def _get_signal(self, row):
        if self.position == 0: # when neutral
            if row[self.price_col] < row["lower"]:  # signal to go long
                return 1
            elif row[self.price_col] > row["upper"]:  # signal to go Short
                return -1
        elif self.position == 1:  # when long
            if row[self.price_col] > row["sma"]:
                if row[self.price_col] > row["upper"]:  # signal to go short
                    return 1
                else:
                    return 0
        elif self.position == -1: # when short
            if row[self.price_col] < row["sma"]:
                if row[self.price_col] < row["lower"]:  # signal to go long
                    return 1
                else:
                    return 0
