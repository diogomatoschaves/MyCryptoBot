import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from quant_model.data_preparation.feature_engineering import get_lag_features, get_rolling_features
from quant_model.modelling.helpers import plot_learning_curve
from quant_model.modelling.model_training import train_model
from quant_model.strategies._mixin import StrategyMixin


class ML(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(
        self,
        estimator,
        data=None,
        lag_features=None,
        rolling_features=None,
        excluded_features=None,
        nr_lags=5,
        windows=(),
        test_size=0.2,
        degree=1,
        print_results=True,
        **kwargs
    ):
        self.estimator = estimator
        self.nr_lags = nr_lags
        self.windows = windows
        self.test_size = test_size
        self.degree = degree
        self.print_results = print_results
        self.lag_features = set(lag_features) \
            if lag_features is not None else None
        self.rolling_features = set(rolling_features) \
            if rolling_features is not None else None
        self.excluded_features = set(excluded_features) \
            if excluded_features is not None else set()

        StrategyMixin.__init__(self, data, **kwargs)

    def __repr__(self):
        return "{}(symbol = {}, estimator = {})".format(self.__class__.__name__, self.symbol, self.estimator)

    def _get_test_title(self):
        return "Testing ML strategy | {} | estimator = {}".format(self.symbol, self.estimator)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """

        data = super(ML, self).update_data(data)
        data = data.drop(columns=self.excluded_features)

        X_lag = self.get_lag_model_x(data)
        X_roll = self.get_rolling_model_x_y(data)
        y = self.get_labels(data)

        self.X, self.y = self.get_x_y(X_lag, X_roll, y)

        self._train_model(self.estimator, self.test_size, self.degree, self.print_results)

        return data

    def set_parameters(self, ml_params=None):
        """ Updates SMA parameters and resp. time series.
        """

        if ml_params is None:
            return

        if not isinstance(ml_params, (tuple, list, type(np.array([])))):
            print(f"Invalid Parameters {ml_params}")
            return

        estimator, test_size, degree, print_results = ml_params

        if estimator is not None:
            self.estimator = estimator
        if test_size is not None:
            self.test_size = test_size
        if degree is not None:
            self.degree = degree
        if print_results is not None:
            self.print_results = print_results

        self.data = self.update_data(self.data)

    @staticmethod
    def get_x_y(X_lag, X_roll, y):

        common_cols = set(X_lag.columns).intersection(set(X_roll.columns))

        X = X_lag.join(X_roll.drop(columns=common_cols), how='inner')
        x_y = X.join(y, how='inner')

        return x_y.iloc[:, :-1].copy(), x_y.iloc[:, -1].copy()

    def get_labels(self, data):
        return data[self.returns_col].shift(-1).dropna().rename('y')

    def get_rolling_model_x_y(self, data):

        rolling_features = self.rolling_features if self.rolling_features is not None else set(data.columns)
        rolling_features = rolling_features.difference(self.excluded_features)

        data = get_rolling_features(data, self.windows, columns=rolling_features)

        return data

    def get_lag_model_x(self, data):

        lag_features = self.lag_features if self.lag_features is not None else set(data.columns)
        lag_features = lag_features.difference(self.excluded_features)

        data = get_lag_features(data, columns=lag_features, n_in=self.nr_lags, n_out=1)

        return data

    def _train_model(
        self,
        estimator,
        test_size=0.2,
        degree=1,
        print_results=True,
        plot_results=True
    ):

        pipeline, X_train, X_test, y_train, y_test = train_model(
            estimator,
            self.X,
            self.y,
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

    def _calculate_positions(self, data):
        """
        Calculates position according to strategy

        :param data:
        :return: data with position calculated
        """
        data["position"] = np.sign(self.pipeline.predict(data))

        return data

    def get_signal(self, row):
        return self.pipeline.predict(pd.DataFrame(row).T)

    def _get_data(self):
        return self.X_test

    def get_values(self, date, row):
        price = self.data.loc[date][self.price_col]

        return price

    def learning_curves(self, metric='accuracy'):

        if not getattr(self, 'pipeline'):
            print("Model hasn't been fitted yet")

        title = "Learning Curves (Gradient Boosting Classifier)"

        tscv = TimeSeriesSplit(n_splits=2)

        training_examples = len(self.X_train)

        train_sizes = [int(n) for n in np.linspace(int(0.05 * training_examples), training_examples, 10)]

        train_sizes, train_scores, test_scores, fit_times = plot_learning_curve(
            self.pipeline, title, self.X_train, self.y_train, train_sizes=np.linspace(0.1, 1, 10), metric=metric
        )