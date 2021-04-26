from model.strategies.mean_reversion import BollingerBands

strategy = BollingerBands
params = {"ma": 7, "sd": 2}
new_parameters = {"ma": 3, "sd": 3}
