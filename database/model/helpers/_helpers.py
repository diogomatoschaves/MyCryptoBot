STRATEGIES = {
    'BollingerBands': {
        "name": "Bollinger Bands",
        "params": ["ma", "sd"]
    },
    'MachineLearning': {
        "name": "Machine Learning",
        "params": [
            "estimator",
            "lag_features",
            "rolling_features",
            "excluded_features",
            "nr_lags",
            "windows",
            "test_size",
            "degree",
            "print_results"
        ]
    },
    'Momentum': {
        "name": "Momentum",
        "params": ["window"]
    },
    'MovingAverageConvergenceDivergence': {
        "name": "Moving Average Convergence Divergence",
        "params": ["window_slow", "window_fast", "window_signal"]
    },
    'MovingAverage': {
        "name": "Moving Average",
        "params": ["sma", "moving_av"]
    },
    'MovingAverageCrossover': {
        "name": "Moving Average Crossover",
        "params": ["SMA_S", "SMA_L", "moving_av"]
    },
}