import numpy as np
from sklearn.model_selection import TimeSeriesSplit

from model.modelling.helpers import plot_learning_curve
from data_processing.transform.feature_engineering import get_lag_features
from model.modelling.model_training import train_model
from strategies.backtesting.vectorized.base import VectorizedBacktester


class MLVectBacktester(VectorizedBacktester):

    def __init__(self, data, estimator, lag_features=None, excluded_features=None, nr_lags=5, trading_costs=0, symbol='BTCUSDT'):

        super().__init__()

        self.data = data.copy()
        self.estimator = estimator
        self.symbol = symbol
        self.nr_lags = nr_lags
        self.tc = trading_costs / 100
        self.lag_features = set(lag_features).add("returns") \
            if isinstance(lag_features, list) else {"returns"}
        self.excluded_features = set(excluded_features).add("close") \
            if excluded_features is not None else {'close'}

        self.pipeline = None
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None

        self._update_data()

    def __repr__(self):
        return "{}(symbol = {}, estimator = {})".format(self.__class__.__name__, self.symbol, self.estimator)

    def _update_data(self):
        """ Retrieves and prepares the data.
        """

        super()._update_data()

        self._get_lag_model_X_y()

    def _set_parameters(self, estimator = None):
        """ Updates SMA parameters and resp. time series.
        """
        if estimator is not None:
            self.estimator = estimator

    def _calculate_position(self, data):
        """
        Calculates position according to strategy

        :param data:
        :return: data with position calculated
        """
        data["position"] = np.sign(self.pipeline.predict(data))

        return data

    def get_rolling_model_df(self):

        pass

    def _get_lag_model_X_y(self):

        data = self.data.copy()
        data.drop(columns=self.excluded_features, inplace=True)

        data = get_lag_features(data, columns=self.lag_features, n_in=self.nr_lags, n_out=1)
        data.dropna(axis=0, inplace=True)

        y = data["returns"].shift(-1).dropna()
        X = data.iloc[:-1].copy()

        self.X = X
        self.y = y

    def test_strategy(self, estimator=None, params=None, test_size=0.2, degree=1, print_results=True, plot_results=True):

        if estimator is not None:
            self._set_parameters(estimator)

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

        title = self.__repr__()

        return self._assess_strategy(X_test, plot_results, title)

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
