import humanfriendly
from scipy.optimize import brute
import plotly.io as pio

from model.backtesting.combining import StrategyCombiner
from model.backtesting.helpers.metrics import *
from model.backtesting.plotting import plot_backtest_results
from shared.utils.exceptions import StrategyRequired, OptimizationParametersInvalid

legend_mapping = {
    "accumulated_returns": "Buy & Hold",
    "accumulated_strategy_returns": "Strategy returns (no trading costs)",
    "accumulated_strategy_returns_tc": "Strategy returns (with trading costs)"
}


results_mapping = {
    'buy_and_hold_return': "Buy & Hold Return [%]",
    'exposure_time': "Exposure Time [%]",
    'equity_final': "Equity Final [USDT]",
    'equity_peak': "Equity Peak [USDT]",
    'return_pct': "Total Return [%]",
    'return_pct_annualized': "Annualized Return [%]",
    'volatility_pct_annualized': "Annualized Volatility [%]",
    'sharpe_ratio': "Sharpe Ratio",
    'sortino_ratio': "Sortino Ratio",
    'calmar_ratio': "Calmar Ratio",
    'max_drawdown': "Max Drawdown [%]",
    'avg_drawdown': "Avg Drawdown [%]",
    'max_drawdown_duration': "Max Drawdown Duration",
    'avg_drawdown_duration': "Avg Drawdown Duration",
    'nr_trades': "Total Trades",
    'win_rate': "Win Rate [%]",
    'best_trade': "Best Trade [%]",
    'worst_trade': "Worst Trade [%]",
    'avg_trade': "Avg Trade [%]",
    'max_trade_duration': "Max Trade Duration",
    'avg_trade_duration': "Avg Trade Duration",
    'profit_factor': "Profit Factor",
    'expectancy': "Expectancy [%]",
    'sqn': "System Quality Number"
}

results_aesthetics = {
    'total_duration': lambda delta: f"\tTotal Duration: {humanfriendly.format_timespan(delta)}",
    'start_date': lambda delta: f"\tStart Date: {delta}",
    'end_date': lambda delta: f"\tEnd Date: {delta}",
    'max_drawdown_duration': lambda delta: f"\tMax Drawdown Duration: {humanfriendly.format_timespan(delta)}",
    'avg_drawdown_duration': lambda sec: f"\tAvg Drawdown Duration: {humanfriendly.format_timespan(timedelta(seconds=sec))}",
    'max_trade_duration': lambda delta: f"\tMax Trade Duration: {humanfriendly.format_timespan(delta)}",
    'avg_trade_duration': lambda sec: f"\tAvg Trade Duration: {humanfriendly.format_timespan(timedelta(seconds=sec))}",
}


pio.renderers.default = "browser"


class BacktestMixin:
    """A Mixin class for backtesting trading strategies.

    Attributes:
    -----------
    symbol : str
        The trading symbol used for the backtest.
    tc : float
        The transaction costs (e.g. spread, commissions) as a percentage.
    results : pandas.DataFrame
        A DataFrame containing the results of the backtest.

    Methods:
    --------
    run(params=None, print_results=True, plot_results=True, plot_positions=False):
        Runs the trading strategy and prints and/or plots the results.
    optimize(params, **kwargs):
        Optimizes the trading strategy using brute force.
    _test_strategy(params=None, print_results=True, plot_results=True, plot_positions=False):
        Tests the trading strategy on historical data.
    _assess_strategy(data, title, print_results=True, plot_results=True, plot_positions=True):
        Assesses the performance of the trading strategy on historical data.
    plot_results(title, plot_positions=True):
        Plots the performance of the trading strategy compared to a buy and hold strategy.
    _gen_repeating(s):
        A generator function that groups repeated elements in an iterable.
    plot_func(ax, group):
        A function used for plotting positions.
    """
    def __init__(self, symbol, amount, trading_costs):
        """
        Initialize the BacktestMixin object.

        Parameters:
        -----------
        symbol : str
            The trading symbol to use for the backtest.
        trading_costs : float
            The transaction costs (e.g. spread, commissions) as a percentage.
        """
        self.amount = amount
        self.symbol = symbol
        self.tc = trading_costs / 100
        self.strategy = None
        self.original_data = None

        self.perf = 0
        self.outperf = 0
        self.results = None

    def __getattr__(self, attr):
        """
        Overrides the __getattr__ method to get attributes from the trading strategy object.

        Parameters
        ----------
        attr : str
            The attribute to be retrieved.

        Returns
        -------
        object
            The attribute object.
        """
        try:
            method = getattr(self.strategy, attr)
            return method
        except AttributeError:
            return getattr(self, attr)

    def load_data(self, data=None, csv_path=None):
        if data is None or csv_path:
            csv_path = csv_path if csv_path else 'model/sample_data/bitcoin.csv'
            data = pd.read_csv(csv_path, index_col='date', parse_dates=True)
            data = data[~data.index.duplicated(keep='last')]  # remove duplicates

        self.original_data = data

        self.set_data(data.copy(), self.strategy)

    def run(self, print_results=True, plot_results=True):
        """Runs the trading strategy and prints and/or plots the results.

        Parameters:
        -----------
        params : dict or None
            The parameters to use for the trading strategy.
        print_results : bool
            If True, print the results of the backtest.
        plot_results : bool
            If True, plot the performance of the trading strategy compared to a buy and hold strategy.

        Returns:
        --------
        None
        """

        perf, outperf, results = self._test_strategy(print_results=print_results, plot_results=plot_results)

        self.perf = perf
        self.outperf = outperf
        self.results = results

    @staticmethod
    def _get_optimization_input(optimization_params, strategy):
        opt_params = []
        for param in strategy.params:
            if param in optimization_params:
                opt_params.append(optimization_params[param])
            else:
                param_value = getattr(strategy, f"_{param}")
                if isinstance(param_value, (float, int)):
                    opt_params.append((param_value, param_value + 1, 1))

        return opt_params

    def _adapt_optimization_input(self, params):

        if not self.strategy:
            raise StrategyRequired

        if isinstance(self.strategy, StrategyCombiner):
            if not isinstance(params, (list, tuple, type(np.array([])))):
                raise OptimizationParametersInvalid('Optimization parameters must be provided as a list'
                                                    ' of dictionaries with the parameters for each individual strategy')

            if len(params) != len(self.strategy.strategies):
                raise OptimizationParametersInvalid(f'Wrong number of parameters. '
                                                    f'Number of strategies is {len(self.strategy.strategies)}')

            opt_params = []
            strategy_params_mapping = []
            for i, strategy in enumerate(self.strategy.strategies):
                strategy_params = self._get_optimization_input(params[i], strategy)
                opt_params.extend(strategy_params)
                strategy_params_mapping.append(len(strategy_params))

            return opt_params, strategy_params_mapping

        else:
            if not isinstance(params, dict):
                raise OptimizationParametersInvalid('Optimization parameters must be provided as a '
                                                    'dictionary with the parameters the strategy')

            return self._get_optimization_input(params, self.strategy), None

    def optimize(self, params, **kwargs):
        """Optimizes the trading strategy using brute force.

        Parameters:
        -----------
        params : dict, list
            A dictionary or list (for strategy combintion) containing the parameters to optimize.
            The parameters must be given as the keywords of a dictionary, and the value is an array
            of the lower limit, upper limit and step, respectively.

            Example for single strategy:
                params = dict(window=(10, 20, 1))

            Example for multiple strategies
                params = [dict(window=(10, 20, 1)), dict(ma=(30, 50, 2)]
        **kwargs : dict
            Additional arguments to pass to the `brute` function.

        Returns:
        --------
        opt : numpy.ndarray
            The optimal parameter values.
        -self._update_and_run(opt, plot_results=True) : float
            The negative performance of the strategy using the optimal parameter values.
        """

        opt_params, strategy_params_mapping = self._adapt_optimization_input(params)

        opt = brute(
            self._update_and_run, opt_params,
            (False, False, strategy_params_mapping),
            finish=None,
            **kwargs
        )

        if not isinstance(opt, (list, tuple, type(np.array([])))):
            opt = np.array([opt])

        return (self._get_params_mapping(opt, strategy_params_mapping),
                -self._update_and_run(opt, True, True, strategy_params_mapping))

    def _test_strategy(self, params=None, print_results=True, plot_results=True):
        """Tests the trading strategy on historical data.

        Parameters:
        -----------
        params : dict or None
            The parameters to use for the trading strategy
        """
        raise NotImplementedError

    def _get_results(self, trades, processed_data):

        total_duration = get_total_duration(processed_data.index)
        start_date = get_start_date(processed_data.index)
        end_date = get_end_date(processed_data.index)

        exposure = exposure_time(processed_data["position"])
        final_equity = equity_final(processed_data["accumulated_strategy_returns_tc"] * self.amount)
        peak_equity = equity_peak(processed_data["accumulated_strategy_returns_tc"] * self.amount)
        buy_and_hold_return = return_buy_and_hold_pct(processed_data["accumulated_returns"])
        pct_return = return_pct(processed_data["accumulated_strategy_returns_tc"])
        annualized_pct_return = return_pct_annualized(processed_data["accumulated_strategy_returns_tc"])
        annualized_pct_volatility = volatility_pct_annualized(processed_data["strategy_returns_tc"])
        sharpe = sharpe_ratio(processed_data["strategy_returns_tc"])
        sortino = sortino_ratio(processed_data["strategy_returns_tc"])
        calmar = calmar_ratio(processed_data["accumulated_strategy_returns_tc"])
        max_drawdown = max_drawdown_pct(processed_data["accumulated_strategy_returns_tc"])
        avg_drawdown = avg_drawdown_pct(processed_data["accumulated_strategy_returns_tc"])
        max_drawdown_dur = max_drawdown_duration(processed_data["accumulated_strategy_returns_tc"])
        avg_drawdown_dur = avg_drawdown_duration(processed_data["accumulated_strategy_returns_tc"])

        nr_trades = int(len(trades))
        win_rate = win_rate_pct(trades)
        best_trade = best_trade_pct(trades)
        worst_trade = worst_trade_pct(trades)
        avg_trade = avg_trade_pct(trades)
        max_trade_dur = max_trade_duration(trades)
        avg_trade_dur = avg_trade_duration(trades)
        profit_fctor = profit_factor(trades)
        expectancy = expectancy_pct(trades)
        sqn = system_quality_number(trades)

        results = pd.Series(
            dict(
                total_duration=total_duration,
                start_date=start_date,
                end_date=end_date,
                nr_trades=nr_trades,
                exposure_time=exposure,
                buy_and_hold_return=buy_and_hold_return,
                return_pct=pct_return,
                equity_final=final_equity,
                equity_peak=peak_equity,
                return_pct_annualized=annualized_pct_return,
                volatility_pct_annualized=annualized_pct_volatility,
                sharpe_ratio=sharpe,
                sortino_ratio=sortino,
                calmar_ratio=calmar,
                max_drawdown=max_drawdown,
                avg_drawdown=avg_drawdown,
                max_drawdown_duration=max_drawdown_dur,
                avg_drawdown_duration=avg_drawdown_dur,
                win_rate=win_rate,
                best_trade=best_trade,
                worst_trade=worst_trade,
                avg_trade=avg_trade,
                max_trade_duration=max_trade_dur,
                avg_trade_duration=avg_trade_dur,
                profit_factor=profit_fctor,
                expectancy=expectancy,
                sqn=sqn
            )
        )

        return results

    def plot_results(self, processed_data, plot_results=True, show_plot_no_tc=False):
        """
        Plot the performance of the trading strategy compared to a buy and hold strategy.

        Parameters:
        -----------
        processed_data: pd.DataFrame
            Dataframe containing the results of the backtest to be plotted.
        plot_results: boolean, default True
            Whether to plot the results.
        show_plot_no_tc: boolean, default False
            Whether to show the plot of the equity curve with no trading costs
        """

        data = processed_data.copy()[[
            "accumulated_returns",
            "accumulated_strategy_returns",
            "accumulated_strategy_returns_tc"
        ]] * self.amount

        trades_df = pd.DataFrame(self.trades)

        if plot_results:
            nr_strategies = len([col for col in processed_data.columns if "position" in col])
            offset = max(0, nr_strategies - 2)

            plot_backtest_results(data, trades_df, offset, show_plot_no_tc=show_plot_no_tc, title=self.__repr__())

    @staticmethod
    def _print_results(results, print_results):
        if print_results:
            print('---------------------------------------')
            print('\tResults')
            print('')
            for col, value in results.items():
                try:
                    print(results_aesthetics[col](value))
                except KeyError:
                    print(f'\t{results_mapping[col]}: {round(value, 2)}')
            print('---------------------------------------')

    def _get_params_mapping(self, parameters, strategy_params_mapping):
        if not isinstance(self.strategy, StrategyCombiner):
            strategy_params = list(self.strategy.get_params().keys())
            new_params = {strategy_params[i]: parameter for i, parameter in enumerate(parameters)}
        else:
            new_params = []

            j = -1
            for i, mapping in enumerate(strategy_params_mapping):
                params = {}
                strategy_params = list(self.strategy.get_params(strategy_index=i).keys())
                for k, j in enumerate(range(j + 1, j + 1 + mapping)):
                    params.update({strategy_params[k]: parameters[j]})

                new_params.append(params)

        return new_params

    def _update_and_run(self, parameters, *args):
        """
        Update the hyperparameters of the strategy with the given `args`,
        and then run the strategy with the updated parameters.
        The strategy is run by calling the `_test_strategy` method with the
        updated parameters.

        Parameters
        ----------
        parameters : array-like
            A list of hyperparameters to be updated in the strategy.
            The order of the elements in the list should match the order
            of the strategy's hyperparameters, as returned by `self.params`.
        plot_results : bool, optional
            Whether to plot the results of the strategy after running it.

        Returns
        -------
        float
            The negative value of the strategy's score obtained with the
            updated hyperparameters. The negative value is returned to
            convert the maximization problem of the strategy's score into
            a minimization problem, as required by optimization algorithms.

        Raises
        ------
        IndexError
            If the number of elements in `parameters` does not match the number
            of hyperparameters in the strategy.

        Notes
        -----
        This method is intended to be used as the objective function to
        optimize the hyperparameters of the strategy using an optimization
        algorithm. It updates the hyperparameters of the strategy with the
        given `parameters`, then runs the strategy with the updated parameters,
        and returns the negative of the score obtained by the strategy.
        The negative is returned to convert the maximization problem of the
        strategy's score into a minimization problem, as required by many
        optimization algorithms.
        """
        print_results, plot_results, strategy_params_mapping = args

        test_params = self._get_params_mapping(parameters, strategy_params_mapping)

        result = self._test_strategy(test_params, print_results=print_results, plot_results=plot_results)

        return -result[0]

    def _fix_original_data(self):
        if self.original_data is None:
            self.original_data = self.strategy.data.copy()

            position_columns = [col for col in self.original_data if "position" in col]

            self.original_data = self.original_data.drop(columns=position_columns)
