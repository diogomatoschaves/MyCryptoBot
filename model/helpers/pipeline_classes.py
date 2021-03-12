import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, PolynomialFeatures

from model.helpers.helper_methods import (
    feature_mapping,
    get_mean_std,
    normalize_features,
)


class FeaturePolynomial(BaseEstimator, TransformerMixin):
    """
    Returns the polynomial terms of features up to a specified degree.
    """

    def __init__(self, order, only_self_terms=True):
        self.order = order
        self.only_self_terms = only_self_terms

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, y=None, **transform_params):

        poly_X = feature_mapping(
            X.to_numpy(), self.order, only_self_terms=self.only_self_terms
        )

        return poly_X


class FeatureNormalizer(BaseEstimator, TransformerMixin):
    """
    Returns the normalized features
    """

    def __init__(self, norm_params_=None):
        self.norm_params_ = norm_params_

    def fit(self, X, y=None, **fit_params):

        if not self.norm_params_:
            self.norm_params_ = get_mean_std(X)

        mean, std = self.norm_params_

        return self

    def transform(self, X, y=None, **transform_params):

        return normalize_features(X, self.norm_params_)


class FeatureSelector(BaseEstimator, TransformerMixin):
    """
    Selects features to be included in the final model.
    """

    def __init__(self, columns, data_type):
        self.data_type = data_type
        self.columns = columns

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, y=None, **transform_params):

        if self.data_type == 'num':

            num_features = list(X.dtypes[(X.dtypes == 'int64') | (X.dtypes == 'float64')].index)
            columns = [col for col in X.columns if col in num_features and col in self.columns]

        elif self.data_type == 'cat':

            cat_features = list(X.dtypes[(X.dtypes != 'int64') & (X.dtypes != 'float64')].index)
            columns = [col for col in X.columns if col in cat_features and col in self.columns]

        else:
            columns = self.columns

        return X.copy()[columns]


class CustomOneHotEncoder(OneHotEncoder):

    def __init__(self, drop=None):
        OneHotEncoder.__init__(self, drop=drop)

    def fit(self, X, y=None, **fit_params):
        self.columns = X.columns
        return super(CustomOneHotEncoder, self).fit(X, y, **fit_params)

    def transform(self, X, y=None, **transform_params):

        transformed_data = super(CustomOneHotEncoder, self).transform(X, **transform_params).toarray()

        return pd.DataFrame(data=transformed_data, columns=self.get_feature_names(self.columns))


class FeatureUnionNames(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None, **fit_params):
        self.features = X.columns

        return self

    def transform(self, X, y=None, **transform_params):
        return X


class CustomStandardScaler(StandardScaler):

    def fit(self, X, y=None, **fit_params):
        self.features = X.columns

        return super(CustomStandardScaler, self).fit(X, y, **fit_params)

    def get_feature_names(self):
        return self.features


class CustomPipeline(Pipeline):

    def get_feature_names(self):
        return self.steps[-1][1].get_feature_names()


class CustomPolynomialFeatures(PolynomialFeatures):

    def fit(self, X, y=None):
        self.columns = X.columns

        return super(CustomPolynomialFeatures, self).fit(X, y)

    def transform(self, X, **transform_params):

        transformed_data = super(CustomPolynomialFeatures, self).transform(X)

        return pd.DataFrame(data=transformed_data, columns=self.get_feature_names(self.columns))
