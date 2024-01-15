import json

import progressbar
from scipy.optimize import brute
import plotly.io as pio

from model.backtesting.combining import StrategyCombiner
from model.backtesting.helpers.metrics import *
from model.backtesting.helpers.results_constants import results_mapping, results_aesthetics, results_sections
from model.backtesting.helpers.plotting import plot_backtest_results
from shared.utils.config_parser import get_config
from shared.utils.exceptions import StrategyRequired, OptimizationParametersInvalid, SymbolInvalid
from shared.utils.exceptions.leverage_invalid import LeverageInvalid

config_vars = get_config('model')

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
    def __init__(
        self,
        symbol,
        amount,
        trading_costs,
        include_margin=False,
        leverage=1,
        exchange='binance'
    ):
        """
        Initialize the BacktestMixin object.

        Parameters:
        -----------
        symbol : str
            The trading symbol to use for the backtest.
        trading_costs : float
            The transaction costs (e.g. spread, commissions) as a percentage.
        """
        self.include_margin = include_margin
        self.exchange = exchange

        self.set_leverage(leverage)

        self.amount = amount
        self.symbol = symbol
        self.tc = trading_costs / 100
        self.strategy = None
        self._original_data = None

        self.perf = 0
        self.outperf = 0
        self.results = None

        if self.include_margin:
            brackets = self._load_leverage_brackets()

            try:
                self._symbol_bracket = pd.DataFrame(brackets[symbol])
            except KeyError:
                raise SymbolInvalid(symbol)

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

    def __repr__(self):
        extra_title = (f"<b>Initial Amount</b> = {self.amount} | "
                       f"<b>Trading Costs</b> = {self.tc * 100}% | "
                       f"<b>Leverage</b> = {self.leverage}")
        return extra_title + '<br>' + self.strategy.__repr__()

    def set_leverage(self, leverage):
        if isinstance(leverage, int) and 1 <= leverage <= 125:
            self.leverage = leverage
        else:
            raise LeverageInvalid(leverage)

    def load_data(self, data=None, csv_path=None):
        if data is None or csv_path:
            csv_path = csv_path if csv_path else config_vars.ohlc_data_file
            data = pd.read_csv(csv_path, index_col='date', parse_dates=True)
            data = data[~data.index.duplicated(keep='last')]  # remove duplicates

        self._original_data = data

        self.set_data(data.copy(), self.strategy)

    def run(self, print_results=True, plot_results=True, leverage=None):
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
        if leverage is not None:
            self.set_leverage(leverage)

        perf, outperf, results = self._test_strategy(print_results=print_results, plot_results=plot_results)

        self.perf = perf
        self.outperf = outperf
        self.results = results

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

        opt_params, strategy_params_mapping, optimization_steps = self._adapt_optimization_input(params)

        self.bar = progressbar.ProgressBar(max_value=optimization_steps, redirect_stdout=True)
        self.optimization_steps = 0

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

    @staticmethod
    def _get_optimization_input(optimization_params, strategy):
        opt_params = []
        optimizations_steps = 1
        for param in strategy.params:
            param_value = getattr(strategy, f"_{param}")
            is_int = isinstance(param_value, int)
            is_float = isinstance(param_value, float)

            step = 1 if is_int else None

            limits = optimization_params[param] \
                if param in optimization_params \
                else (param_value, param_value + 1) if is_int or is_float \
                else None

            if limits is not None:
                params = (*limits, step) if step is not None else limits
                opt_params.append(params)

                optimizations_steps *= (limits[1] - limits[0])

        return opt_params, optimizations_steps

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
            optimization_steps = 1
            for i, strategy in enumerate(self.strategy.strategies):
                strategy_params, opt_steps = self._get_optimization_input(params[i], strategy)
                opt_params.extend(strategy_params)
                strategy_params_mapping.append(len(strategy_params))

                optimization_steps *= opt_steps

            return opt_params, strategy_params_mapping, optimization_steps

        else:
            if not isinstance(params, dict):
                raise OptimizationParametersInvalid('Optimization parameters must be provided as a '
                                                    'dictionary with the parameters the strategy')

            strategy_params, optimization_steps = self._get_optimization_input(params, self.strategy)

            return strategy_params, None, optimization_steps

    def _get_results(self, trades, processed_data):

        total_duration = get_total_duration(processed_data.index)
        start_date = get_start_date(processed_data.index)
        end_date = get_end_date(processed_data.index)

        leverage = self.leverage
        trading_costs = self.tc * 100
        initial_equity = self.amount
        exposed_capital = initial_equity / leverage

        exposure = exposure_time(processed_data["side"])
        final_equity = equity_final(processed_data["accumulated_strategy_returns_tc"] * self.amount)
        peak_equity = equity_peak(processed_data["accumulated_strategy_returns_tc"] * self.amount)
        buy_and_hold_return = return_buy_and_hold_pct(processed_data["accumulated_returns"]) * leverage
        pct_return = return_pct(processed_data["accumulated_strategy_returns_tc"]) * leverage
        annualized_pct_return = return_pct_annualized(processed_data["accumulated_strategy_returns_tc"], leverage)
        annualized_pct_volatility = volatility_pct_annualized(
            processed_data["strategy_returns_tc"],
            config_vars.trading_days
        )

        sharpe = sharpe_ratio(processed_data["strategy_returns_tc"], trading_days=config_vars.trading_days)
        sortino = sortino_ratio(processed_data["strategy_returns_tc"])
        calmar = calmar_ratio(processed_data["accumulated_strategy_returns_tc"])
        max_drawdown = max_drawdown_pct(processed_data["accumulated_strategy_returns_tc"])
        avg_drawdown = avg_drawdown_pct(processed_data["accumulated_strategy_returns_tc"])
        max_drawdown_dur = max_drawdown_duration(processed_data["accumulated_strategy_returns_tc"])
        avg_drawdown_dur = avg_drawdown_duration(processed_data["accumulated_strategy_returns_tc"])

        nr_trades = int(len(trades))
        win_rate = win_rate_pct(trades)
        best_trade = best_trade_pct(trades, leverage)
        worst_trade = worst_trade_pct(trades, leverage)
        avg_trade = avg_trade_pct(trades, leverage)
        max_trade_dur = max_trade_duration(trades)
        avg_trade_dur = avg_trade_duration(trades)
        profit_fctor = profit_factor(trades)
        expectancy = expectancy_pct(trades)
        sqn = system_quality_number(trades)

        results = pd.Series(
            dict(
                total_duration=total_duration,
                nr_trades=nr_trades,
                start_date=start_date,
                end_date=end_date,
                trading_costs=trading_costs,
                leverage=leverage,
                initial_equity=initial_equity,
                exposed_capital=exposed_capital,
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

        columns = [
            "accumulated_returns",
            "accumulated_strategy_returns",
            "accumulated_strategy_returns_tc",
        ]

        data = processed_data.copy()[columns] * self.amount

        if self.include_margin:
            data["margin_ratios"] = processed_data["margin_ratios"].copy() * 100

        trades_df = pd.DataFrame(self.trades)

        if plot_results:
            nr_strategies = len([col for col in processed_data.columns if "side" in col])
            offset = max(0, nr_strategies - 2)

            title = self.__repr__()

            plot_backtest_results(
                data,
                trades_df,
                offset,
                plot_margin_ratio=self.include_margin,
                show_plot_no_tc=show_plot_no_tc,
                title=title
            )

    @staticmethod
    def _print_results(results, print_results):
        if not print_results:
            return

        length = 50

        print()

        print('*' * length)
        print('BACKTESTING RESULTS'.center(length))
        print('*' * length)
        print('')

        for section, columns in results_sections.items():

            # print('-' * length)
            print(section.center(length))
            print('-' * length)

            for col in columns:

                value = results[col]

                if callable(results_mapping[col]):
                    printed_title = results_mapping[col]('USDT')
                else:
                    printed_title = results_mapping[col]

                if col in results_aesthetics:
                    value = results_aesthetics[col](value)
                else:
                    try:
                        value = str(round(value, 2))
                    except TypeError:
                        value = str(value)

                print(f'{printed_title:<25}{value.rjust(25)}')
            print('-' * length)
            print()
        print('*' * length)

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

        self.optimization_steps += 1

        try:
            self.bar.update(self.optimization_steps)
        except ValueError:
            pass

        return -result[0]

    def _fix_original_data(self):
        if self._original_data is None:
            self._original_data = self.strategy.data.copy()

            position_columns = [col for col in self._original_data if "side" in col]

            self._original_data = self._original_data.drop(columns=position_columns)

    @staticmethod
    def _load_leverage_brackets():

        filepath = config_vars.leverage_brackets_file
        with open(filepath, 'r') as f:
            data = json.load(f)

        brackets = {symbol["symbol"]: symbol["brackets"] for symbol in data}

        return brackets
