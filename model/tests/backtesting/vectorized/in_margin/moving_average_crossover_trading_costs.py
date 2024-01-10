from model.strategies.moving_average import MovingAverageCrossover

strategy = MovingAverageCrossover
params = {"sma_s": 4, "sma_l": 7}
trading_costs = 0.3
optimization_params = {"sma_s": (1, 10, 1), "sma_l": (1, 10, 1)}
