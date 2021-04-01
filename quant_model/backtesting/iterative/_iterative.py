from quant_model.backtesting.iterative._mixin import IterativeBacktesterMixin


class IterativeBacktester(IterativeBacktesterMixin):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, data, sub_class, params, amount=1000, symbol='BTCUSDT', trading_costs=0, **kwargs):

        IterativeBacktester.__bases__ = (sub_class,) + IterativeBacktester.__bases__ \
            if sub_class not in IterativeBacktester.__bases__ \
            else IterativeBacktester.__bases__

        IterativeBacktesterMixin.__init__(self, amount, symbol=symbol, trading_costs=trading_costs)
        sub_class.__init__(self, data, *params, **kwargs)
