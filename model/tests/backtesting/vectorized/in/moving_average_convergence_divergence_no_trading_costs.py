from model.strategies.moving_average import MovingAverageConvergenceDivergence

strategy = MovingAverageConvergenceDivergence
params = {"window_fast": 3, "window_slow": 6, "window_signal": 4}
trading_costs = 0
optimization_params = {
    "window_fast": (1, 4, 1),
    "window_slow": (4, 7, 1),
    "window_signal": (2, 5, 1),
}
