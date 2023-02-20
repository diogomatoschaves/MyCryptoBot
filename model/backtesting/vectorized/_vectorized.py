from model.backtesting._mixin import BacktestMixin


class VectorizedBacktester(BacktestMixin):
    """ Class for vectorized backtesting.
    """

    def __init__(self, strategy, symbol='BTCUSDT', trading_costs=0):
        """

        Parameters
        ----------
        strategy : StrategyType
            A valid strategy class as defined in model.strategies __init__ file.
        symbol : string
            Symbol for which we are performing the backtest.
        trading_costs : int
            The trading cost per trade in percentage of the value being traded.
        """

        BacktestMixin.__init__(self, symbol, trading_costs)

        self.strategy = strategy

    def __repr__(self):
        return self.strategy.__repr__()

    def _test_strategy(self, params=None, print_results=True, plot_results=True, plot_positions=False):
        """

        Parameters
        ----------
        params : dict
            Dictionary containing the keywords and respective values of the parameters to be updated.
        plot_results: boolean
            Flag for whether to plot the results of the backtest.
        plot_positions : boolean
            Flag for whether to plot the positions markers on the results plot.

        """

        self.set_parameters(params)

        title = self.__repr__()

        data = self._get_data().dropna().copy()

        return self._assess_strategy(data, title, print_results, plot_results, plot_positions)

    def _get_trades(self, data):
        return data.trades.sum()
