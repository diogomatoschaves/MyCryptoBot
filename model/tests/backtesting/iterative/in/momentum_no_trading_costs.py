from model.strategies.trend import Momentum

strategy = Momentum
params = {"window": 4}
trading_costs = 0
optimization_params = {"window": (1, 10)}
