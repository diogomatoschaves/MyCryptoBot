from strategies.backtesting.iterative.base import IterativeBacktester
from strategies.backtesting.strategies import MomentumBase


class MomentumIterBacktester(MomentumBase, IterativeBacktester):

    def __init__(self, data, amount, window):
        MomentumBase.__init__(self)
        IterativeBacktester.__init__(self, data, amount)

        self.window = window

        self._update_data()

    def _get_signal(self, row):
        if row["rolling_returns"] >= 0:
            return 1
        else:
            return -1

    def _get_test_title(self):
        return "Testing Momentum strategy | {} | window: {}".format(self.symbol, self.window)
