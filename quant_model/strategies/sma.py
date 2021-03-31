

class SMABase:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, sma):
        self.data = None
        self.sma = sma
        self.symbol = None

    def __repr__(self):
        return "{}(symbol = {}, SMA = {})".format(self.__class__.__name__, self.symbol, self.sma)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """

        data["SMA"] = data["close"].rolling(self.sma).mean()

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

    def get_signal(self, row):
        if row["SMA"] > row[self.price_col]:
            return 1
        elif row["SMA"] < row[self.price_col]:
            return -1
