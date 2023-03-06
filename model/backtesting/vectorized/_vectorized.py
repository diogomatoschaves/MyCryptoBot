import numpy as np
from model.backtesting._mixin import BacktestMixin


class VectorizedBacktester(BacktestMixin):
    """ Class for vectorized backtesting.
    """

    def __init__(self, strategy, symbol=None, trading_costs=0.0):
        """

        Parameters
        ----------
        strategy : StrategyType
            A valid strategy class as defined in model.strategies __init__ file.
        symbol : string
            Symbol for which we are performing the backtest. default is None.
        trading_costs : int
            The trading cost per trade in percentage of the value being traded.
        """

        BacktestMixin.__init__(self, symbol, trading_costs)

        self.strategy = strategy
        self.strategy.symbol = symbol

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

        data = self._get_data().dropna().copy()

        if data.empty:
            return 0, 0

        self._vectorized_backtest(data)

        nr_trades, perf, outperf = self._evaluate_backtest()

        self._print_results(nr_trades, perf, outperf, print_results)

        self.plot_results(self.results, plot_results, plot_positions)

        return perf, outperf

    def _vectorized_backtest(self, data):
        """
        Assess the performance of the trading strategy on historical data.

        Parameters:
        -----------
        data : pandas.DataFrame
            Historical price data for the trading symbol. Pre sanitized.

        Returns:
        --------
        None
        """
        data = self._calculate_positions(data)
        data["trades"] = data.position.diff().fillna(0).abs()

        data["strategy_returns"] = data.position.shift(1) * data.returns
        data["strategy_returns_tc"] = data["strategy_returns"] - data["trades"] * self.tc

        data.dropna(inplace=True)

        data["accumulated_returns"] = data[self.returns_col].cumsum().apply(np.exp)
        data["accumulated_strategy_returns"] = data["strategy_returns"].cumsum().apply(np.exp)
        data["accumulated_strategy_returns_tc"] = data["strategy_returns_tc"].cumsum().apply(np.exp)

        self.results = data

    def _evaluate_backtest(self):
        """
       Evaluates the performance of the trading strategy on the backtest run.

       Parameters:
       -----------
       print_results : bool, default True
           Whether to print the results.

       Returns:
       --------
       float
           The performance of the strategy.
       float
           The out-/underperformance of the strategy.
       """

        data = self.results

        nr_trades = self._get_trades(data)

        # absolute performance of the strategy
        perf = data["accumulated_strategy_returns_tc"].iloc[-1]

        # out-/underperformance of strategy
        outperf = perf - data["accumulated_returns"].iloc[-1]

        return nr_trades, perf, outperf

    def _get_trades(self, data):
        return int(data["trades"].sum() / 2)
