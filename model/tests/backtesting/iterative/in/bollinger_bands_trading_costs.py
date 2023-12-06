from model.strategies.mean_reversion import BollingerBands

strategy = BollingerBands
params = {"ma": 3, "sd": 1}
trading_costs = 0.1
optimization_params = {"ma": (1, 8, 1), "sd": (1, 5, 1)}
