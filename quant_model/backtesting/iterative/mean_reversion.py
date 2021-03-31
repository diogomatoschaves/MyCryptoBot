from quant_model.backtesting.iterative.base import IterativeBacktester
from quant_model.strategies import MeanRev


class MeanRevIterBacktester(MeanRev, IterativeBacktester):

    def __init__(self, data, amount, ma, sd, trading_costs=0, symbol='BTCUSDT'):
        MeanRev.__init__(self, ma, sd)
        IterativeBacktester.__init__(
            self,
            data,
            amount,
            symbol=symbol,
            trading_costs=trading_costs
        )

        self.data = self.update_data(self.data)

    def _get_test_title(self):
        return "Testing Bollinger Bands Strategy: {} | ma = {} & sd = {}".format(self.symbol, self.ma, self.sd)
