import numpy as np
from sklearn.model_selection import TimeSeriesSplit

from model.modelling.helpers import plot_learning_curve
from model.modelling.model_training import train_model
from strategies.backtesting.strategies import MLBase
from strategies.backtesting.vectorized.base import VectorizedBacktester


class MLVectBacktester(MLBase, VectorizedBacktester):

    def __init__(self, data, estimator, lag_features=None, excluded_features=None, nr_lags=5, trading_costs=0, symbol='BTCUSDT'):

        MLBase.__init__(self)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.estimator = estimator
        self.nr_lags = nr_lags
        self.lag_features = set(lag_features).add(self.returns_col) \
            if isinstance(lag_features, list) else {self.returns_col}
        self.excluded_features = set(excluded_features).add(self.price_col) \
            if excluded_features is not None else {self.price_col}

        self._update_data()

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
