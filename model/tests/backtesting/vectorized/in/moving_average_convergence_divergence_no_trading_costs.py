from model.strategies.moving_average import MovingAverageConvergenceDivergence

strategy = MovingAverageConvergenceDivergence
params = {"window_fast": 3, "window_slow": 6, "window_sign": 4}
trading_costs = 0
optimization_params = {
    "window_fast": (1, 4),
    "window_slow": (4, 7),
    "window_sign": (2, 5),
}
