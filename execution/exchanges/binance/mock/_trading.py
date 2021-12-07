import shared.exchanges.binance.constants as const
from execution.exchanges.binance._trading import BinanceTrader
from execution.tests.setup.test_data.binance_api_responses import order_creation, trading_fees, isolated_account_info


class BinanceMockTrader(BinanceTrader):

    def __init__(
        self,
        margin_level=3,
    ):
        BinanceTrader.__init__(
            self,
            margin_level=margin_level,
            paper_trading=True
        )

        self.create_test_order()

    def _init_session(self):
        pass

    def ping(self):
        pass

    def get_isolated_margin_account(self):
        return isolated_account_info

    def create_margin_loan(self, asset, amount, isIsolated, symbol):
        return {"tranId": 100000001}

    def get_trade_fee(self, symbol):
        return trading_fees

    def get_max_margin_loan(self, asset, isolatedSymbol):
        return {"amount": "1.69248805", "borrowLimit": "60"}

    def repay_margin_loan(self, asset, amount, isIsolated, symbol):
        return {"tranId": 100000001}

    def create_margin_order(
            self,
            symbol,
            side,
            type,
            newOrderRespType,
            isIsolated,
            sideEffectType,
            quantity=None,
            quoteOrderQty=None,
    ):
        if newOrderRespType == "FULL":
            return order_creation