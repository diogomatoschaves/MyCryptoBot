from quant_model.backtesting.iterative.base import IterativeBacktester
from quant_model.strategies import MACrossover


class MACrossoverIterBacktester(MACrossover, IterativeBacktester):

    def __init__(self, data, amount, SMA_S, SMA_L, trading_costs=0, symbol='BTCUSDT', moving_av='sma', **kwargs):
        MACrossover.__init__(self, SMA_S, SMA_L, moving_av, **kwargs)
        IterativeBacktester.__init__(self, data, amount, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | SMA_S = {} & SMA_L = {}".format(self.symbol, self.SMA_S, self.SMA_L)
