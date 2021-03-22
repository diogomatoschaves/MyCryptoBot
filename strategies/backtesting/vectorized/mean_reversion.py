import numpy as np

from strategies.backtesting.strategies import MeanRevBase
from strategies.backtesting.vectorized.base import VectorizedBacktester


class MeanRevVectBacktester(MeanRevBase, VectorizedBacktester):
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
        MeanRevBase.__init__(self)
        VectorizedBacktester.__init__(self, data, trading_costs=trading_costs, symbol=symbol)

        self.ma = ma
        self.sd = sd

        self._update_data()

    def test_strategy(self, ma_sd_pair=None, plot_results=True):
        """ Backtests the trading strategy.
        """

        self._set_parameters(ma_sd_pair)

        data = self.data.copy().dropna()
        data["distance"] = data[self.price_col] - data["sma"]
        data["position"] = np.where(data[self.price_col] > data["upper"], -1, np.nan)
        data["position"] = np.where(data[self.price_col] < data["lower"], 1, data["position"])
        data["position"] = np.where(data["distance"] * data["distance"].shift(1) < 0, 0, data["position"])
        data["position"] = data["position"].ffill().fillna(0)

        title = self.__repr__()

        return self._assess_strategy(data, title, plot_results)
