import shared.exchanges.binance.constants as const
from execution.exchanges.binance._trading import BinanceTrader


class BinanceMockTrader(BinanceTrader):

    def __init__(
        self,
        symbol='BTCUSDT',
        margin_level=3,
        paper_trading=False
    ):
        BinanceTrader.__init__(
            self,
            account=const.BINANCE_SPOT_TRADING,
            symbol=symbol,
            margin_level=margin_level,
            paper_trading=paper_trading
        )

        self.create_test_order()

    def create_margin_order(
        self,
        symbol,
        side,
        type,
        newOrderRespType,
        isIsolated,
        sideEffectType,
        **kwargs
    ):
        pass

    def _get_assets_info(self):
        pass

    # def _get_symbol_net_equity(self, symbol):
    #     pass
    #
    # def _get_max_borrow_amount(self):
    #     pass
    #
    # def _create_initial_loan(self):
    #     pass
