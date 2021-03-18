import logging
import joblib

import numpy as np
from sklearn.base import is_classifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline, FeatureUnion

from model.modelling.helpers import train_test_split_ts
from utils.logger import configure_logger
from model.modelling.helpers import FeatureSelector, CustomOneHotEncoder, CustomStandardScaler, CustomPipeline, CustomPolynomialFeatures
from model.modelling.defaults import (
    estimator_params,
)
from model.modelling.model_evaluation import model_evaluation

grid_search_params_defaults = {
    "reg__n_estimators": [250, 300, 350],
    "reg__min_samples_split": [2, 4, 5],
    "reg__max_features": ["sqrt", "log2", "auto"],
    "reg__max_depth": [2, 3, 5, 6],
}

configure_logger()


def save_model(model, model_filepath):
    """
    Saves the model as a pickle file
    :param model: the ML model to be saved
    :param model_filepath: path pointing to where the file should be saved
    :return: None
    """

    joblib.dump(model, model_filepath)


def load_model(model_filepath):
    """
    Loads the model from a pickle file

    :param model_filepath: path pointing to the saved model
    :return: the loaded model
    """

    model = joblib.load(model_filepath)

    return model


def build_pipeline(
    estimator_name,
    estimator_params_override=None,
    grid_search=False,
    grid_search_params=None,
    degree=1
):
    """
    Builds the pipeline required to fit the features into the model
    :param estimator_name: regressor name. Default will be Ridge
    :param grid_search: If grid search should be performed
    :param grid_search_params: extra params to be passed to the grid search
    :return: the built model
    """

    if not grid_search_params:
        grid_search_params = {}

    try:
        if not estimator_params_override:
            estimator_params_override = {}

        params = {**estimator_params[estimator_name], ** estimator_params_override}

        estimator = eval(estimator_name)(**params)
    except NameError:
        raise Exception(f"{estimator_name} is not a valid Estimator")

    is_clf = is_classifier(estimator)

    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('num_features', CustomPipeline([
                ('selector', FeatureSelector('num')),
                ('feature_polynomials', CustomPolynomialFeatures(degree=degree, include_bias=False)),
                ('scaling', CustomStandardScaler())
            ])),
            ('cat_features', CustomPipeline([
                ('selector', FeatureSelector('cat')),
                ('one-hot-encoder', CustomOneHotEncoder(drop='first'))
            ]))
        ])),
        ('estimator', estimator),
    ])

    if grid_search:
        param_grid = {}

        if len(grid_search_params) == 0 and estimator in (
            RandomForestRegressor,
            GradientBoostingRegressor,
        ):
            param_grid.update(grid_search_params_defaults)
        else:
            param_grid.update(grid_search_params)

        pipeline = GridSearchCV(pipeline, param_grid=param_grid, n_jobs=-1, cv=3)

    return pipeline, is_clf


def train_model(
    estimator_name,
    X,
    y,
    estimator_params_override=None,
    grid_search=False,
    evaluation_metric=None,
    print_results=True,
    plot_results=True,
    test_size=0.2,
    degree=1
):
    """
    Handles all the logic to build a machine learning pipeline, train the data and
    evaluate the model.

    :param df: preprocessed data frame containing the training data
    :param grid_search: whether to perform grid search on the model or not
    :return: the fitted model
    """

    logging.info("\tbuilding model...")

    model, is_clf = build_pipeline(
        estimator_name,
        estimator_params_override=estimator_params_override,
        # num_features=num_features,
        # cat_features=cat_features,
        grid_search=grid_search,
        degree=degree
    )

    if is_clf:
        y = np.sign(y)

    X_train, X_test, y_train, y_test = train_test_split_ts(X, y, test_size=test_size)

    if grid_search:
        logging.info("\tPerforming grid search...")
    else:
        logging.info("\tfitting data...")

    model.fit(X_train, y_train)

    logging.info("\tevaluating model...")

    model_evaluation(
        model,
        X_test,
        y_test,
        X_train,
        y_train,
        is_clf=is_clf,
        evaluation_metric=evaluation_metric,
        grid_search=grid_search,
        print_results=print_results,
        plot_results=plot_results
    )

    return model, X_train, X_test, y_train, y_test
