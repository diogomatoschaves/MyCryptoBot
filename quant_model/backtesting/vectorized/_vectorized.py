from quant_model.backtesting.vectorized._mixin import VectorizedBacktesterMixin


class VectorizedBacktester(VectorizedBacktesterMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, sub_class, params, symbol='BTCUSDT', trading_costs=0, **kwargs):

        VectorizedBacktester.__bases__ = (sub_class,) + VectorizedBacktester.__bases__ \
            if sub_class not in VectorizedBacktester.__bases__ \
            else VectorizedBacktester.__bases__

        VectorizedBacktesterMixin.__init__(self, symbol=symbol, trading_costs=trading_costs)
        sub_class.__init__(self, data, *params, **kwargs)
