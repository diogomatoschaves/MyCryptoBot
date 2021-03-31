import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brute

from quant_model.backtesting.base import BacktestBase


class VectorizedBacktester(BacktestBase):
    """ Class for the vectorized backtesting.

    """

    def __init__(self, data, symbol, trading_costs=0, price_col='close', returns_col='returns'):
        BacktestBase.__init__(self)

        self.data = data.copy()
        self.tc = trading_costs / 100
        self.symbol = symbol
        self.price_col = price_col
        self.returns_col = returns_col
        self.results = None

        self._calculate_returns()

    def test_strategy(self, params=None, plot_results=True):
        """ Backtests the trading strategy.
        """

        self._set_parameters(params)

        # data = self.data.dropna().copy()

        # data["position"] = np.where(data["SMA"] > data[self.price_col], 1, -1)

        title = self.__repr__()

        return self._assess_strategy(self.data, title, plot_results)

    def _set_parameters(self, *args):
        """ Updates parameters.
        """
        raise NotImplementedError

    def _calculate_positions(self, data):
        """
        Calculates position according to strategy

        :param data:
        :return: data with position calculated
        """
        return data

    def _get_trades(self, data):
        return data.trades.sum()

    def _update_and_run(self, *args, plot_results=False):
        """ Updates SMA parameters and returns the negative absolute performance (for minimization algorithm).

        Parameters
        ==========
        SMA: tuple
            SMA parameter tuple
        """
        return -self.test_strategy(*args, plot_results)[0]

    def optimize_parameters(self, *opt_params, **kwargs):
        ''' Finds global maximum given the SMA parameter ranges.

        Parameters
        ==========
        SMA1_range, SMA2_range: tuple
            tuples of the form (start, end, step size)
        '''

        opt = brute(self._update_and_run, opt_params, finish=None)

        return opt, -self._update_and_run(opt, plot_results=True)

