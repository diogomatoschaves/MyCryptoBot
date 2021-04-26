from model.strategies.moving_average import MovingAverageCrossover

strategy = MovingAverageCrossover
params = {"sma_s": 3, "sma_l": 10}
new_parameters = {"sma_s": 3, "sma_l": 6}
