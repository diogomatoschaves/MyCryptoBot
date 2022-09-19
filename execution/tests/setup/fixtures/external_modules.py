from random import randint

import pytest

import execution
from execution.tests.setup.test_data.binance_api_responses import (
    isolated_account_info,
    trading_fees,
    order_creation,
)


def binance_client_mock_factory(method, type_='mock'):
    class MockBinanceHandler(object):

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
                return {**order_creation, "orderId": randint(0, 1E9)}

    @pytest.fixture
    def mock_binance_client(mocker):
        return mocker.patch.object(
            execution.exchanges.binance.margin._trading.BinanceMarginTrader, method, getattr(MockBinanceHandler, method)
        )

    @pytest.fixture
    def spy_binance_client(mocker):
        return mocker.spy(
            execution.exchanges.binance.margin._trading.BinanceMarginTrader, method
        )

    if type_ == 'mock':
        return mock_binance_client

    elif type_ == 'spy':
        return spy_binance_client


def binance_mock_trader_spy_factory(method):
    @pytest.fixture
    def spy_binance_client(mocker):
        return mocker.spy(
            execution.exchanges.binance.margin.mock._trading.BinanceMockMarginTrader, method
        )

    return spy_binance_client

