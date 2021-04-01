from quant_model.backtesting.iterative.base import IterativeBacktester
from quant_model.strategies import ML


class MLIterBacktester(ML, IterativeBacktester):

    def __init__(
        self,
        data,
        amount,
        estimator,
        lag_features=None,
        excluded_features=None,
        nr_lags=5,
        params=None,
        test_size=0.2,
        degree=1,
        print_results=True,
        trading_costs=0,
        symbol='BTCUSDT',
    ):
        IterativeBacktester.__init__(self, data, amount, symbol=symbol, trading_costs=trading_costs)
        ML.__init__(self, estimator, lag_features, excluded_features, nr_lags, params, test_size, degree, print_results)

        self.data = self.update_data(self.data)

    def get_values(self, date, row):
        price = self.data.loc[date][self.price_col]

        return price

    def _get_test_title(self):
        return "Testing ML strategy | {} | estimator = {}".format(self.symbol, self.estimator)
