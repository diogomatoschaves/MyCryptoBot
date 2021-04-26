from model.strategies.moving_average import MovingAverageConvergenceDivergence

strategy = MovingAverageConvergenceDivergence
params = dict(window_slow=9, window_fast=5, window_signal=3)
new_parameters = dict(window_slow=6, window_fast=4, window_signal=2)
