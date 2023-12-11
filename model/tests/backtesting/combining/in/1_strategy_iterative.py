from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverageCrossover

strategy = MovingAverageCrossover(2, 6)

strategies = [strategy]

method = "Unanimous"

backtester = VectorizedBacktester
