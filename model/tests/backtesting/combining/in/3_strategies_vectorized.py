from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverageCrossover, Momentum, BollingerBands

strategy_1 = MovingAverageCrossover(2, 6)
strategy_2 = Momentum(5)
strategy_3 = BollingerBands(5, 1)

strategies = [strategy_1, strategy_2, strategy_3]

method = "Unanimous"

backtester = VectorizedBacktester
