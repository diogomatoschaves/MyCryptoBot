import pandas as pd

from model.modelling.model_training import train_model
from strategies.backtesting.iterative.base import IterativeBacktester
from strategies.backtesting.strategies import MLBase


class MLIterBacktester(MLBase, IterativeBacktester):

    def __init__(
        self,
        data,
        amount,
        estimator,
        lag_features=None,
        excluded_features=None,
        nr_lags=5,
        trading_costs=0,
        symbol='BTCUSDT',
        params=None,
        test_size=0.2,
        degree=1,
        print_results=True,
    ):
        MLBase.__init__(self)
        IterativeBacktester.__init__(self, data, amount, symbol=symbol, trading_costs=trading_costs)

        self.estimator = estimator
        self.params = params
        self.test_size = test_size
        self.degree = degree
        self.print_results = print_results

        self.nr_lags = nr_lags
        self.lag_features = set(lag_features).add(self.returns_col) \
            if isinstance(lag_features, list) else {self.returns_col}
        self.excluded_features = set(excluded_features).add(self.price_col) \
            if excluded_features is not None else {self.price_col}

        self._update_data()

    def get_values(self, date, row):
        price = self.data.loc[date][self.price_col]

        return price

    def _get_signal(self, row):
        return self.pipeline.predict(pd.DataFrame(row).T)

    def _get_test_title(self):
        return "Testing ML strategy | {} | estimator = {}".format(self.symbol, self.estimator)

    def _get_data(self):
        return self.X_test

    def _reset_object(self):
        super(MLIterBacktester, self)._reset_object()

        self._train_model(
            self.estimator,
            self.params,
            self.test_size,
            self.degree,
            self.print_results
        )
