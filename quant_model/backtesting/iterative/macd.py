from quant_model.strategies import MACD
from quant_model.backtesting.iterative.base import IterativeBacktester


class MACDIterBacktester(MACD, IterativeBacktester):

    def __init__(
        self,
        data,
        amount,
        window_slow=26,
        window_fast=12,
        window_signal=9,
        trading_costs=0,
        symbol='BTCUSDT',
        **kwargs
    ):
        MACD.__init__(self, window_slow, window_fast, window_signal, **kwargs)
        IterativeBacktester.__init__(self, data, amount, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)

    def _get_test_title(self):
        return "Testing SMA strategy | {} | fast = {}, slow = {}, signal = {}".format(
            self.symbol, self._window_fast, self._window_slow, self._window_sign
        )
