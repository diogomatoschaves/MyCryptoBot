import numpy as np
from scipy.optimize import brute

from model.backtesting._mixin import BacktestMixin


class VectorizedBacktester(BacktestMixin):
    """ Class for vectorized backtesting.
    """

    def __init__(self, strategy, symbol='BTCUSDT', trading_costs=0):

        BacktestMixin.__init__(self, symbol, trading_costs)

        self.strategy = strategy

    def __repr__(self):
        return self.strategy.__repr__()

    def __getattr__(self, attr):
        method = getattr(self.strategy, attr)

        if not method:
            return getattr(self, attr)
        else:
            return method

    def test_strategy(self, params=None, plot_results=True):
        """ Backtests the trading strategy.
        """

        self.set_parameters(params)

        title = self.__repr__()

        data = self._get_data().dropna().copy()

        return self._assess_strategy(data, title, plot_results)

    def _get_trades(self, data):
        return data.trades.sum()

    def _update_and_run(self, args, plot_results=False):

        params = {}
        for i, arg in enumerate(args):
            params[list(self.params.items())[i][0]] = arg

        return -self.test_strategy(params, plot_results=plot_results)[0]

    def optimize_parameters(self, params, **kwargs):

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
