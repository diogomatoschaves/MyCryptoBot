import os
import time
from random import randint

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import StructuredData
from execution.exchanges.binance.margin._trading import BinanceMarginTrader
from execution.tests.setup.test_data.binance_api_responses import trading_fees, isolated_account_info


class BinanceMockMarginTrader(BinanceMarginTrader):

    def __init__(
        self,
        margin_level=3,
    ):
        BinanceMarginTrader.__init__(
            self,
            margin_level=margin_level,
            paper_trading=True
        )

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
        **kwargs
    ):
        transact_time = int(time.time() * 1000)

        price = StructuredData.objects.last().close

        quantity = quantity if quantity else quoteOrderQty

        return {
            "symbol": symbol,
            "orderId": randint(1, 1E9),
            "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
            "transactTime": transact_time,
            "price": str(price),
            "origQty": str(quantity),
            "executedQty": str(quantity),
            "cummulativeQuoteQty": str(quantity),
            "status": "FILLED",
            "timeInForce": "GTC",
            "type": "MARKET",
            "side": side,
            "isIsolated": True,  # if isolated margin
            "fills": [
                {
                    "price": str(price),
                    "qty": str(quantity),
                    "commission": str(0.001 * price),
                    "commissionAsset": "USDT",
                },
            ],
        }
