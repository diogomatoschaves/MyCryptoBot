import numpy as np
from sklearn.model_selection import TimeSeriesSplit

from model.modelling.helpers import plot_learning_curve
from quant_model.strategies import ML
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class MLVectBacktester(ML, VectorizedBacktester):

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
        trading_costs=0,
        symbol='BTCUSDT'
    ):

        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)
        ML.__init__(self, estimator, lag_features, excluded_features, nr_lags, params, test_size, degree, print_results)

        self.data = self.update_data(self.data)

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
