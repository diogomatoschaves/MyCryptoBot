from quant_model.backtesting.iterative.base import IterativeBacktester
from quant_model.strategies import MA


class MAIterBacktester(MA, IterativeBacktester):

    def __init__(self, data, amount, sma, trading_costs=0, symbol='BTCUSDT', moving_av='sma', **kwargs):
        MA.__init__(self, sma, moving_av, **kwargs)
        IterativeBacktester.__init__(self, data, amount, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | SMA_S = {}".format(self.symbol, self.sma)
