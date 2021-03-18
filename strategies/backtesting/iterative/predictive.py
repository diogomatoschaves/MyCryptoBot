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
        symbol='BTCUSDT'
    ):
        MLBase.__init__(self)
        IterativeBacktester.__init__(self, data, amount, symbol=symbol, trading_costs=trading_costs)

        self.estimator = estimator
        self.nr_lags = nr_lags
        self.lag_features = set(lag_features).add(self.returns_col) \
            if isinstance(lag_features, list) else {self.returns_col}
        self.excluded_features = set(excluded_features).add(self.price_col) \
            if excluded_features is not None else {self.price_col}

        self._update_data()

    def get_values(self, data, bar):
        date = data.iloc[bar:].index[0]
        return date, self.data.loc[date][self.price_col]

    def test_strategy(
        self,
        estimator=None,
        params=None,
        test_size=0.2,
        degree=1,
        print_results=True,
        plot_results=True
    ):

        self._set_parameters(estimator)
        self._reset_object()

        # nice printout
        print("-" * 75)
        print("Testing ML strategy | {} | estimator = {}".format(self.symbol, self.estimator))
        print("-" * 75)

        pipeline, X_train, X_test, y_train, y_test = train_model(
            self.estimator,
            self.X,
            self.y,
            estimator_params_override=params,
            degree=degree,
            print_results=print_results,
            plot_results=plot_results,
            test_size=test_size
        )

        self.pipeline = pipeline
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

        for bar, (timestamp, row) in enumerate(X_test.iloc[:-1].iterrows()):

            date, price = self.get_values(X_test, bar)

            prediction = pipeline.predict(pd.DataFrame(row).T)

            if prediction == 1:
                if self.position in [0, -1]:
                    self.go_long(date, price, amount="all")
                    self.position = 1
            elif prediction == -1:
                if self.position in [0, 1]:
                    self.go_short(date, price, amount="all")
                    self.position = -1

            self.positions.append(self.position)

        self.close_pos(X_test, bar + 1)

        self.positions.append(0)

        title = self.__repr__()

        return self._assess_strategy(X_test, title, plot_results)
