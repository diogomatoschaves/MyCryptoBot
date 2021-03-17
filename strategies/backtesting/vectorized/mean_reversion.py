import numpy as np

from strategies.backtesting.vectorized.base import VectorizedBacktester


class MeanRevBacktester(VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.

    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    ma: int
        time window in days for shorter SMA
    sd: int
        time window in days for longer SMA

    """

    def __init__(self, data, ma, sd, trading_costs=0, symbol='BTCUSDT'):

        super().__init__()

        self.data = data.copy()
        self.ma = ma
        self.sd = sd
        self.symbol = symbol
        self.tc = trading_costs
        self.results = None

        self._update_data()

    def __repr__(self):
        return "{}(symbol = {}, ma = {}, sd = {})".format(self.__class__.__name__, self.symbol, self.ma, self.sd)

    def _update_data(self):
        """ Retrieves and prepares the data.
        """

        super()._update_data()

        data = self.data
        data["sma"] = data["close"].rolling(self.ma).mean()
        data["upper"] = data["sma"] + data["close"].rolling(self.ma).std() * self.sd
        data["lower"] = data["sma"] - data["close"].rolling(self.ma).std() * self.sd

        self.data = data

    def _set_parameters(self, ma = None, sd = None):
        """ Updates SMA parameters and resp. time series.
        """
        if ma is not None:
            self.ma = int(ma)
        if sd is not None:
            self.sd = sd

        self._update_data()

    def test_strategy(self, ma_sd_pair=None, plot_results=True):
        """ Backtests the trading strategy.
        """
        if ma_sd_pair is not None and isinstance(ma_sd_pair, (tuple, list, type(np.array([])))):
            self._set_parameters(*ma_sd_pair)

        data = self.data.copy().dropna()
        data["distance"] = data["close"] - data["sma"]
        data["position"] = np.where(data["close"] > data["upper"], -1, np.nan)
        data["position"] = np.where(data["close"] < data["lower"], 1, data["position"])
        data["position"] = np.where(data["distance"] * data["distance"].shift(1) < 0, 0, data["position"])
        data["position"] = data["position"].ffill().fillna(0)

        title = self.__repr__()

        return self._assess_strategy(data, plot_results, title)
