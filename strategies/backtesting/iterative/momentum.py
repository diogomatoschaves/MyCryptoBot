from strategies.backtesting.iterative.base import IterativeBacktester
from strategies.strategies import MomentumBase


class MomentumIterBacktester(MomentumBase, IterativeBacktester):

    def __init__(self, data, amount, window):
        MomentumBase.__init__(self, window)
        IterativeBacktester.__init__(self, data, amount)

        self.data = self.update_data(self.data)

    def _get_test_title(self):
        return "Testing Momentum strategy | {} | window: {}".format(self.symbol, self.window)
