import calendar

import numpy as np
from pandas import CategoricalDtype

from quant_model.modelling.helpers.ts_differencing import ts_differencing


def add_returns_features(df):

    df["returns"] = df.close.pct_change()

    df["diff"] = df.close.diff()

    df["partial_diff"] = ts_differencing(df["close"], 0.4, 10)

    df["log_returns"] = np.log(df.close / df.close.shift(1))

    df["returns_class"] = df["returns"].apply(lambda x: 1 if x > 0 else -1).astype('category')

    return df


def add_date_variables(df):

    df = df.copy()

    df["hour"] = df.index.hour
    df["weekday"] = df.index.day_name()
    df["week"] = df.index.isocalendar().week
    df["month_name"] = df.index.month_name()
    df["month"] = df.index.day
    df["month"] = df.month.apply(lambda day: "beginning" if day <= 10 else "end" if day > 20 else "middle")

    hours = CategoricalDtype(categories=range(24), ordered=True)
    df.hour = df.hour.astype(hours)

    weekdays = CategoricalDtype(categories=list(calendar.day_name), ordered=True)
    df.weekday = df.weekday.astype(weekdays)

    week = CategoricalDtype(categories=[n for n in range(1, 54)], ordered=True)
    df.week = df.week.astype(week)

    months = CategoricalDtype(categories=list(calendar.month_name)[1:], ordered=True)
    df.month_name = df.month_name.astype(months)

    return df


def add_extra_variables(df):

    df = df.copy()

    df["range"] = (df["high"] - df["low"]) / df["low"]

    return df


def get_lag_features(df, columns=None, n_in=1, n_out=1, dropnan=True):
    """
    Frame a time series as a supervised learning dataset.
    Arguments:
        df: Sequence of observations as a list or NumPy array.
        n_in: Number of lag observations as input (X).
        n_out: Number of observations as output (y).
        dropnan: Boolean whether or not to drop rows with NaN values.
    Returns:
        Pandas DataFrame of series framed for supervised learning.
    """

    original_df = df.copy()
    df = df.copy()

    if columns is None:
        columns = df.columns

    how = {"how": 'inner' if dropnan else 'outer'}

    for i in range(n_in, -n_out, -1):

        if i == 0:
            continue

        df = df.join(original_df[columns].shift(i), rsuffix=f"_{'lag' if i > 0 else 'fwd'}{i}", **how)

    if dropnan:
        df.dropna(axis=0, inplace=True)

    return df


def get_rolling_features(df, windows, columns=None, statistics='mean', mav='sma', dropnan=True):

    if not isinstance(windows, (list, tuple, type(np.array([])))):
        windows = [windows]

    if not isinstance(statistics, (list, tuple, type(np.array([])))):
        statistics = [statistics]

    if columns is None:
        columns = df.columns

    df = df.copy()

    for stat in statistics:
        for window in windows:

            if mav == 'sma':
                moving_av = df[columns].rolling(window=window)
            elif mav == 'ema':
                moving_av = df[columns].ewm(span=window)
            else:
                raise('Method not supported')

            df = df.join(
                getattr(moving_av, stat)(),
                rsuffix=f'_{mav}_{window}_{stat}',
            )

    if dropnan:
        df.dropna(axis=0, inplace=True)

    return df


def engineer_features(df):

    df = add_returns_features(df)

    df = add_date_variables(df)

    df = add_extra_variables(df)

    return df
