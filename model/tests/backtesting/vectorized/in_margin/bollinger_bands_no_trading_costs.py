from model.strategies.mean_reversion import BollingerBands

strategy = BollingerBands
params = {"ma": 4, "sd": 1}
trading_costs = 0
optimization_params = {"ma": (3, 6), "sd": (1, 3)}
