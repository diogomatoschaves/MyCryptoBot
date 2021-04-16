from model.strategies.trend import Momentum
from model.strategies.moving_average import MovingAverageConvergenceDivergence
from model.strategies.moving_average import MovingAverageCrossover
from model.strategies.moving_average import MovingAverage
from model.strategies.mean_reversion import BollingerBands
from model.strategies.machine_learning import MachineLearning

from model.strategies._strategies import get_signal, trigger_order
