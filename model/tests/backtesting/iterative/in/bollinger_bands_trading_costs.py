from model.strategies.mean_reversion import BollingerBands

strategy = BollingerBands
params = {"ma": 3, "sd": 1}
trading_costs = 0.1
