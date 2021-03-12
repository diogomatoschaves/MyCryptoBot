import numpy as np
from sklearn.model_selection import TimeSeriesSplit

from model.helpers.helper_methods import series_to_supervised, plot_learning_curve
from model.model_training import train_model


class MLBacktester:

    def __init__(self, data, lag_features, other_features, target, nr_lags=5, trading_costs=0):
        self.data = data.copy()
        self.nr_lags = nr_lags
        self.tc = trading_costs / 100
        self.lag_features = lag_features
        self.other_features = other_features
        self.target = target
        self.returns_var = 'log_returns_target'

        self.get_lag_model_df()

    def get_lag_model_df(self):

        data = self.data.copy()

        model_features = [*self.lag_features, *self.other_features]

        other_features = [*self.other_features, self.target]
        if self.returns_var not in [*other_features, *self.lag_features]:
            other_features.append(self.returns_var)

        data = series_to_supervised(data[self.lag_features], self.nr_lags, 1).join(data[other_features], how='left')
        data.dropna(axis=0, inplace=True)

        cat_features = list(data.dtypes[(data.dtypes != 'int64') & (data.dtypes != 'float64')].index)

        excluded_vars = {*cat_features, self.target, self.returns_var if self.returns_var not in model_features else None}

        num_features = [col for col in data.columns if col not in excluded_vars]

        data["direction"] = np.sign(data[self.returns_var])

        self.data = data
        self.num_features = num_features
        self.cat_features = cat_features

    def test_strategy(self, estimator, params=None, test_size=0.2, degree=1, print_results=True, plot_predictions=True):

        self.train_model(estimator, params=params, test_size=test_size, degree=degree, print_results=True, plot_predictions=True)
        self.assess_strategy()
        self.assess_strategy(dataset='train')

    def assess_strategy(self, dataset='test'):
        X = getattr(self, f'X_{dataset}')
        y = getattr(self, f'y_{dataset}')

        hits = np.sign(y * X.pred).value_counts()
        accuracy = hits[1.0] / hits.sum()

        X["trades"] = X.pred.diff().fillna(0).abs()

        X["strategy"] = X.pred * X[self.returns_var]
        X["strategy_tc"] = X["strategy"] - np.abs(X[self.returns_var]) * X.trades * self.tc

        X["creturns"] = X[self.returns_var].cumsum().apply(np.exp)
        X["cstrategy"] = X["strategy"].cumsum().apply(np.exp)
        X["cstrategy_tc"] = X["strategy_tc"].cumsum().apply(np.exp)

        plotting_cols = ["creturns", "cstrategy"]
        if self.tc != 0:
            plotting_cols.append("cstrategy_tc")

        X[plotting_cols].plot(figsize = (15 , 10))

        number_trades = X.trades.value_counts()[2.0]

        print(f"Accuracy: {accuracy}")
        print(f"Numer of trades: {number_trades}")

    def train_model(self, estimator, params=None, test_size=0.2, degree=1, print_results=True, plot_predictions=True):

        pipeline, X_train, X_test, y_train, y_test = train_model(
            self.data,
            estimator,
            self.num_features,
            self.cat_features,
            self.target,
            estimator_params_override=params,
            degree=degree,
            print_results=print_results,
            plot_predictions=plot_predictions,
            test_size=test_size
        )

        X_test = X_test.copy()
        X_train = X_train.copy()

        X_test["pred"] = np.sign(pipeline.predict(X_test))
        X_train["pred"] = np.sign(pipeline.predict(X_train))
        self.data["pred"] = np.sign(pipeline.predict(self.data))

        self.pipeline = pipeline
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

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