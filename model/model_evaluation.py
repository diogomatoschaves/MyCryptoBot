import logging

import matplotlib.pyplot as plt

import seaborn as sb
from sklearn.metrics import (mean_absolute_error,
                             mean_squared_error, r2_score, f1_score, precision_score, recall_score)


base_color = sb.color_palette()[0]


def plot_predictions(y_test, y_pred, target, is_clf):

    if is_clf:

        equal = y_test[y_pred == y_test]
        not_equal = y_test[y_pred != y_test]

        plt.figure(figsize=(15, 10))
        plt.bar(x=equal.index, height=equal, width=0.1, color='limegreen', label='Correct Predictions')
        plt.bar(x=not_equal.index, height=not_equal, width=0.1, color='r', label='Wrong Predictions')
        plt.yticks((-1, 1), ('Negative returns', 'Positive returns'))
        plt.title(f'{target.replace("_", " ")}: Predictions')
        plt.legend()

    else:

        plt.figure(figsize=(15, 10))
        plt.bar(x=y_test.index, height=y_test, width=0.3, color='deepskyblue', label='Real')
        plt.bar(x=y_test.index, height=y_pred, width=0.3, color='r', label='Prediction')
        plt.title(f'{target.replace("_", " ")}: Real vs Predicted')
        plt.legend()


def model_evaluation(
    model,
    X_test,
    y_test,
    X_train,
    y_train,
    target,
    is_clf,
    evaluation_metric=None,
    grid_search=False,
    print_results=True,
    plot_results=True
):
    """
    Wrapper around the model evaluation steps.

    :param model: fitted model
    :param X_test: test features data frame
    :param y_test: test target data frame
    :param grid_search: whether to perform grid search or not
    :return:
    """

    if grid_search:
        logging.info(f"\t\tbest estimator: {model.best_estimator_}")
        logging.info(f"\t\tbest params: {model.best_params_}")
        logging.info(f"\t\tbest score: {model.best_score_}")

        return

    y_pred = model.predict(X_test)

    if print_results:

        if is_clf:
            f1 = f1_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)

            logging.info(f"\t\tF1 score: {f1}")
            logging.info(f"\t\tRecall: {recall}")
            logging.info(f"\t\tPrecision: {precision}")

        else:
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)

            logging.info(f"\t\tR2 score: {r2}")
            logging.info(f"\t\tMean absolute error: {mae}")
            logging.info(f"\t\tMean squared error: {mse}")

    if plot_results:
        plot_predictions(y_test, y_pred, target, is_clf)
