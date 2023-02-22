import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import brute

legend_mapping = {
    "creturns": "Hold & Buy",
    "cstrategy": "Strategy returns (no trading costs)",
    "cstrategy_tc": "Strategy returns (with trading costs)"
}


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
    def __init__(self, symbol, trading_costs):
        """
        Initialize the BacktestMixin object.

        Parameters:
        -----------
        symbol : str
            The trading symbol to use for the backtest.
        trading_costs : float
            The transaction costs (e.g. spread, commissions) as a percentage.
        """
        self.symbol = symbol
        self.tc = trading_costs / 100
        self.strategy = None

        self.perf = 0
        self.outperf = 0

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
        method = getattr(self.strategy, attr)

        if not method:
            return getattr(self, attr)
        else:
            return method

    def load_data(self, data=None, csv_path=None):
        if data:
            self.set_data(data, self.strategy)

        if csv_path or not data:
            csv_path = csv_path if csv_path else 'model/sample_data/bitcoin.csv'
            self.set_data(pd.read_csv(csv_path, index_col='date'), self.strategy)

    def run(self, params=None, print_results=True, plot_results=True, plot_positions=False):
        """Runs the trading strategy and prints and/or plots the results.

        Parameters:
        -----------
        params : dict or None
            The parameters to use for the trading strategy.
        print_results : bool
            If True, print the results of the backtest.
        plot_results : bool
            If True, plot the performance of the trading strategy compared to a buy and hold strategy.
        plot_positions : bool
            If True, plot the trading positions.

        Returns:
        --------
        None
        """
        perf, outperf = self._test_strategy(params, print_results, plot_results, plot_positions)

        self.perf = perf
        self.outperf = outperf

    def optimize(self, params, **kwargs):
        """Optimizes the trading strategy using brute force.

        Parameters:
        -----------
        params : dict
            A dictionary containing the parameters to optimize.
        **kwargs : dict
            Additional arguments to pass to the `brute` function.

        Returns:
        --------
        opt : numpy.ndarray
            The optimal parameter values.
        -self._update_and_run(opt, plot_results=True) : float
            The negative performance of the strategy using the optimal parameter values.
        """
        opt_params = []
        for param in self.params:
            if param in params:
                opt_params.append(params[param])
            else:
                param_value = getattr(self, f"_{param}")
                if isinstance(param_value, (float, int)):
                    opt_params.append((param_value, param_value + 1, 1))

        opt = brute(self._update_and_run, opt_params, finish=None)

        if not isinstance(opt, (list, tuple, type(np.array([])))):
            opt = np.array([opt])

        return opt, -self._update_and_run(opt, plot_results=True)

    def _test_strategy(self, params=None, print_results=True, plot_results=True, plot_positions=False):
        """Tests the trading strategy on historical data.

        Parameters:
        -----------
        params : dict or None
            The parameters to use for the trading strategy
        """
        raise NotImplementedError

    def plot_results(self, plot_results=True, plot_positions=True):
        """
        Plot the performance of the trading strategy compared to a buy and hold strategy.

        Parameters:
        -----------
        title : str
            Title for the plot.
        plot_results: boolean, default True
            Whether to plot the results.
        plot_positions : bool, default True
            Whether to plot the positions.
        """

        if not plot_results:
            return

        try:
            _ = self.results
        except AttributeError:
            print("No results to plot yet. Run the strategy first.")
            return

        plotting_cols = ["creturns"]
        if self.tc != 0:
            plotting_cols.append("cstrategy")

        title = self.__repr__()

        ax = self.results[plotting_cols].plot(title=title, figsize=(12, 8))\

        if plot_positions:

            # Convert labels to colors
            label2color = {
                1: 'green',
                0: 'brown',
                -1: 'red',
            }
            self.results['color'] = self.results['position'].apply(lambda label: label2color[label])

            # Add px_last lines
            for color, start, end in self._gen_repeating(self.results['color']):
                if start > 0: # make sure lines connect
                    start -= 1
                idx = self.results.index[start:end+1]
                self.results.loc[idx, 'cstrategy_tc'].plot(ax=ax, color=color, label='')
                self.results.loc[idx, ['position']].plot(ax=ax, color=color, label='', secondary_y='position', alpha=0.3)

            # Get artists and labels for legend and chose which ones to display
            handles, labels = ax.get_legend_handles_labels()

            # Create custom artists
            g_line = plt.Line2D((0, 1), (0, 0), color='green')
            y_line = plt.Line2D((0, 1), (0, 0), color='brown')
            r_line = plt.Line2D((0, 1), (0, 0), color='red')

            # Create legend from custom artist/label lists
            ax.legend(
                handles + [g_line, y_line, r_line],
                labels + [
                    'long position',
                    'neutral_position',
                    'short position',
                ],
                loc='best',
            )

        else:
            ax.plot(self.results.index, self.results["cstrategy_tc"], c='g')

            plotting_cols.append("cstrategy_tc")

            ax.legend([legend_mapping[col] for col in plotting_cols])

        plt.show()

    @staticmethod
    def _gen_repeating(s):
        """
        A generator function that groups repeated elements in an iterable.

        Parameters:
        -----------
        s : Iterable
            An iterable object.

        Yields:
        -------
        Tuple
            A tuple containing the element, start index, and end index of a group of repeated elements.
        """
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s.iloc[j] == s.iloc[i]:
                j += 1
            yield (s.iloc[i], i, j-1)
            i = j

    @staticmethod
    def plot_func(ax, group):
        color = 'r' if (group['position'] < 0).all() else 'g'
        lw = 2.0
        ax.plot(group.index, group.cstrategy_tc, c=color, linewidth=lw)

    @staticmethod
    def _print_results(nr_trades, perf, outperf, print_results):
        if print_results:
            print('--------------------------------')
            print('\tResults')
            print('')
            print(f'\t# Trades: {nr_trades}')
            print(f'\tPerformance: {perf}')
            print(f'\tOut Performance: {outperf}')
            print('--------------------------------')

    def _update_and_run(self, args, plot_results=False):
        """
        Update the hyperparameters of the strategy with the given `args`,
        and then run the strategy with the updated parameters.
        The strategy is run by calling the `_test_strategy` method with the
        updated parameters.

        Parameters
        ----------
        args : array-like
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
            If the number of elements in `args` does not match the number
            of hyperparameters in the strategy.

        Notes
        -----
        This method is intended to be used as the objective function to
        optimize the hyperparameters of the strategy using an optimization
        algorithm. It updates the hyperparameters of the strategy with the
        given `args`, then runs the strategy with the updated parameters,
        and returns the negative of the score obtained by the strategy.
        The negative is returned to convert the maximization problem of the
        strategy's score into a minimization problem, as required by many
        optimization algorithms.
        """

        params = {}
        for i, arg in enumerate(args):
            params[list(self.params.items())[i][0]] = arg

        return -self._test_strategy(params, print_results=False, plot_results=plot_results)[0]
