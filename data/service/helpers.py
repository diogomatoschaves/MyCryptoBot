STRATEGIES = {
    'BollingerBands': {
        "params": {"ma", "sd"}
    },
    'MachineLearning': {
        "params": {
            "estimator",
            "lag_features",
            "rolling_features",
            "excluded_features",
            "nr_lags",
            "windows",
            "test_size",
            "degree",
            "print_results"
        }
    },
    'Momentum': {
        "params": {"window"}
    },
    'MovingAverageConvergenceDivergence': {
        "params": {"window_slow", "window_fast", "window_signal"}
    },
    'MovingAverage': {
        "params": {"sma", "moving_av"}
    },
    'MovingAverageCrossover': {
        "params": {"SMA_S", "SMA_L", "moving_av"}
    },
}