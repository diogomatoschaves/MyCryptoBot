import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from data_processing.transform.feature_engineering import get_lag_features
from model.modelling.helpers import plot_learning_curve
from model.modelling.model_training import train_model
from quant_model.strategies.mixin import StrategyMixin


class ML(StrategyMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(
        self,
        data,
        estimator,
        lag_features=None,
        excluded_features=None,
        nr_lags=5,
        params=None,
        test_size=0.2,
        degree=1,
        print_results=True,
    ):
        self.data = data.copy()

        self.estimator = estimator
        self.nr_lags = nr_lags
        self.params = params
        self.test_size = test_size
        self.degree = degree
        self.print_results = print_results
        self.lag_features = {*set(lag_features), self.returns_col} \
            if isinstance(lag_features, list) else {self.returns_col}
        self.excluded_features = {*set(excluded_features), self.price_col} \
            if excluded_features is not None else {self.price_col}

        self.pipeline = None
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None

        self.data = self.update_data(self.data)

    def __repr__(self):
        return "{}(symbol = {}, estimator = {})".format(self.__class__.__name__, self.symbol, self.estimator)

    def _get_test_title(self):
        return "Testing ML strategy | {} | estimator = {}".format(self.symbol, self.estimator)

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """

        self._calculate_returns()

        self._get_lag_model_X_y(data.copy())

        self._train_model(self.estimator, self.params, self.test_size, self.degree, self.print_results)

        return data

    def _set_parameters(self, ml_params=None):
        """ Updates SMA parameters and resp. time series.
        """

        if ml_params is None:
            return

        if not isinstance(ml_params, (tuple, list, type(np.array([])))):
            print(f"Invalid Parameters {ml_params}")
            return

        estimator, params, test_size, degree, print_results = ml_params

        if estimator is not None:
            self.estimator = estimator
        if params is not None:
            self.params = params
        if test_size is not None:
            self.test_size = test_size
        if degree is not None:
            self.degree = degree
        if print_results is not None:
            self.print_results = print_results

        self.data = self.update_data(self.data)

    def get_rolling_model_df(self):

        pass

    def _get_lag_model_X_y(self, data):

        data.drop(columns=self.excluded_features, inplace=True)

        data = get_lag_features(data, columns=self.lag_features, n_in=self.nr_lags, n_out=1)
        data.dropna(axis=0, inplace=True)

        y = data[self.returns_col].shift(-1).dropna()
        X = data.iloc[:-1].copy()

        self.X = X
        self.y = y

    def _train_model(self, estimator, params=None, test_size=0.2, degree=1, print_results=True, plot_results=True):

        pipeline, X_train, X_test, y_train, y_test = train_model(
            estimator,
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