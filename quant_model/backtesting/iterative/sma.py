from quant_model.backtesting.iterative.base import IterativeBacktester
from quant_model.strategies import SMABase


class SMAIterBacktester(SMABase, IterativeBacktester):

    def __init__(self, data, amount, sma, trading_costs=0, symbol='BTCUSDT'):
        SMABase.__init__(self, sma)
        IterativeBacktester.__init__(self, data, amount, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | SMA_S = {}".format(self.symbol, self.sma)
