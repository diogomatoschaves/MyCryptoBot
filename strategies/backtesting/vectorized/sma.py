import numpy as np

from strategies.backtesting.vectorized.base import VectorizedBacktester


class SMAVectBacktester(VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.

    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    SMA_S: int
        time window in days for shorter SMA
    SMA_L: int
        time window in days for longer SMA

    Methods
    =======
    get_data:
        retrieves and prepares the data

    set_parameters:
        sets one or two new SMA parameters

    test_strategy:
        runs the backtest for the SMA-based strategy

    plot_results:
        plots the performance of the strategy compared to buy and hold

    update_and_run:
        updates SMA parameters and returns the negative absolute performance (for minimization algorithm)

    optimize_parameters:
        implements a brute force optimization for the two SMA parameters
    """

    def __init__(self, data, SMA_S, SMA_L, trading_costs=0, symbol='BTCUSDT'):
        super().__init__(data, symbol=symbol, trading_costs=trading_costs)

        self.SMA_S = SMA_S
        self.SMA_L = SMA_L

        self._update_data()

    def __repr__(self):
        return "{}(symbol = {}, SMA_S = {}, SMA_L = {})".format(self.__class__.__name__, self.symbol, self.SMA_S, self.SMA_L)

    def _update_data(self):
        """ Retrieves and prepares the data.
        """

        super()._update_data()

        data = self.data

        data["SMA_S"] = data["close"].rolling(self.SMA_S).mean()
        data["SMA_L"] = data["close"].rolling(self.SMA_L).mean()

        self.data = data

    def _set_parameters(self, SMA_S = None, SMA_L = None):
        """ Updates SMA parameters and resp. time series.
        """
        if SMA_S is not None:
            self.SMA_S = int(SMA_S)
            self.data["SMA_S"] = self.data["close"].rolling(self.SMA_S).mean()
        if SMA_L is not None:
            self.SMA_L = int(SMA_L)
            self.data["SMA_L"] = self.data["close"].rolling(self.SMA_L).mean()

    def test_strategy(self, sma=None, plot_results=True):
        """ Backtests the trading strategy.
        """
        if sma is not None and isinstance(sma, (tuple, list, type(np.array([])))):
            self._set_parameters(sma[0], sma[1])

        data = self.data.copy()
        data["position"] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)

        title = self.__repr__()

        return self._assess_strategy(data, plot_results, title)
