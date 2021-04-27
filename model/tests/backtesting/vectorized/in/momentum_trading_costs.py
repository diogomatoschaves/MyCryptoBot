from model.strategies.trend import Momentum

strategy = Momentum
params = {"window": 4}
trading_costs = 0.1
optimization_params = {"window": (1, 10, 1)}
