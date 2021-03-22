from strategies.backtesting.iterative.base import IterativeBacktester
from strategies.backtesting.strategies import MeanRevBase


class MeanRevIterBacktester(MeanRevBase, IterativeBacktester):

    def __init__(self, data, amount, ma, sd, trading_costs=0, symbol='BTCUSDT'):
        MeanRevBase.__init__(self)
        IterativeBacktester.__init__(
            self,
            data,
            amount,
            symbol=symbol,
            trading_costs=trading_costs
        )

        self.ma = ma
        self.sd = sd
        self.results = None

        self._update_data()

    def _get_signal(self, row):
        if self.position == 0: # when neutral
            if row[self.price_col] < row["lower"]:  # signal to go long
                return 1
            elif row[self.price_col] > row["upper"]:  # signal to go Short
                return -1
        elif self.position == 1:  # when long
            if row[self.price_col] > row["sma"]:
                if row[self.price_col] > row["upper"]:  # signal to go short
                    return 1
                else:
                    return 0
        elif self.position == -1: # when short
            if row[self.price_col] < row["sma"]:
                if row[self.price_col] < row["lower"]:  # signal to go long
                    return 1
                else:
                    return 0

    def _get_test_title(self):
        return "Testing Bollinger Bands Strategy: {} | ma = {} & sd = {}".format(self.symbol, self.ma, self.sd)
