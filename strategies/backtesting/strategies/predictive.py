import numpy as np

from data_processing.transform.feature_engineering import get_lag_features
from model.modelling.model_training import train_model


class MLBase:
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self):
        self.data = None
        self.price_col = None
        self.returns_col = None
        self.symbol = None
        self.nr_lags = None

        self.lag_features = None
        self.excluded_features = None

        self.pipeline = None
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None

    def __repr__(self):
        return "{}(symbol = {}, estimator = {})".format(self.__class__.__name__, self.symbol, self.estimator)

    def _update_data(self):
        """ Retrieves and prepares the data.
        """

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