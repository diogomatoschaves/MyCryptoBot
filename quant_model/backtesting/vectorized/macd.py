from quant_model.strategies import MACD
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class MACDVectBacktester(MACD, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(
        self,
        data,
        window_slow=26,
        window_fast=12,
        window_signal=9,
        trading_costs=0,
        symbol='BTCUSDT',
        **kwargs
    ):
        MACD.__init__(self, window_slow, window_fast, window_signal, **kwargs)
        VectorizedBacktester.__init__(self, data, symbol=symbol, trading_costs=trading_costs)

        self.data = self.update_data(self.data)
