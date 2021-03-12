import os
import sys

import pandas as pd
from fitfeats.feature_optimization import FeatureOptimizer
from sklearn.model_selection import TimeSeriesSplit

from backtesting.ml_backtester import MLBacktester

df = pd.read_csv('data/bitcoin_clean.csv', parse_dates=[0], index_col=0)

target = 'returns_class_target'

other_features = ['hour', 'weekday', 'month']

excluded_cols = ['id', 'asset', 'open', 'high', 'close', 'low', 'price_btc', 'sentiment_absolute',
                 'returns', 'diff', 'partial_diff', 'returns_class', 'returns_target',
                 'log_returns_target', 'diff_target', 'partial_diff_target', 'returns_class_target',
                 'close_target', 'hour', 'weekday', 'week', 'month_name', 'month',]

lag_features = [col for col in df.columns if col not in excluded_cols]

estimator = 'GradientBoostingClassifier'
params = dict(n_estimators=1000, max_depth=1)

ml_tester = MLBacktester(df, lag_features, other_features, target, 0, trading_costs=0.1)
ml_tester.test_strategy(estimator, params=params, test_size=0.1, degree=1)

tscv = TimeSeriesSplit(n_splits=3)

fo = FeatureOptimizer(
    ml_tester.pipeline,
    cv=tscv,
    scoring='accuracy',
    max_gen=10,
    pop_size=10,
    selection_rate=0.5,
    mutation_rate=0.1,
    selection_strategy="roulette_wheel",
    n_jobs=-1,
)

fo.fit(ml_tester.X_train[[*lag_features, *other_features]], ml_tester.y_train, feature_subset_include=['log_returns'])

