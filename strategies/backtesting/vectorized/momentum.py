import numpy as np

from strategies.backtesting.vectorized.base import VectorizedBacktester


class MomentumVectBacktester(VectorizedBacktester):
    """ Class for the vectorized backtesting of simple Contrarian trading strategies.

    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    start: str
        start date for data retrieval
    end: str
        end date for data retrieval
    tc: float
        proportional transaction costs per trade

    Methods
    =======
    get_data:
        retrieves and prepares the data

    test_strategy:
        runs the backtest for the contrarian-based strategy

    plot_results:
        plots the performance of the strategy compared to buy and hold
    """

    def __init__(self, data, window=10, trading_costs=0, symbol='BTC'):
        super().__init__()

        self.data = data.copy()
        self.window = window
        self.symbol = symbol
        self.tc = trading_costs / 100
        self.results = None

        self._update_data()

    def __repr__(self):
        return "{}(symbol = {}, window = {})".format(self.__class__.__name__, self.symbol, self.window)

    def _update_data(self):
        """ Retrieves and prepares the data.
        """
        super()._update_data()

    def _set_parameters(self, window):
        """ Updates SMA parameters and resp. time series.
        """
        if window is not None:
            self.window = int(window)

    def test_strategy(self, window=None, plot_results=True):
        """ Backtests the trading strategy.
        """
        self._set_parameters(window)

        data = self.data.copy().dropna()
        data["position"] = np.sign(data["returns"].rolling(self.window).mean())

        title = self.__repr__()

        return self._assess_strategy(data, plot_results, title)
