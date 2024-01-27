from random import randint

import pytest

import execution
from execution.exchanges.binance.futures import BinanceFuturesTrader
from execution.tests.setup.test_data.binance_api_responses import (
    isolated_account_info,
    trading_fees,
    margin_order_creation, futures_order_creation, exchange_info, account_balances, positions_info,
)


class MockBinanceHandler(BinanceFuturesTrader):

    def _init_session(self):
        return None

    def ping(self):
        return None

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
            return {**margin_order_creation, "orderId": randint(0, 1E9)}

    def futures_change_leverage(self, symbol, leverage):
        return {'symbol': symbol, 'leverage': leverage, 'maxNotionalValue': 'INF'}

    def futures_create_order(self, symbol, side, type, newOrderRespType, quantity, **kwargs):
        return {
            **futures_order_creation,
            "symbol": symbol,
            "side": side,
            "type": type,
            "origQty": quantity,
            "orderId": randint(0, 1E9)
        }

    def futures_account_balance(self):
        return account_balances

    def futures_symbol_ticker(self, symbol):

        tickers = {
            "BTCUSDT": 40000,
        }

        if symbol in tickers:
            return {'symbol': symbol, 'price': tickers.get(symbol)}

    def futures_position_information(self):
        return positions_info


def binance_client_mock_factory(method, type_='mock', account_type='margin'):

    @pytest.fixture
    def mock_binance_margin_client(mocker):
        return mocker.patch.object(
            execution.exchanges.binance.margin._trading.BinanceMarginTrader, method, getattr(MockBinanceHandler, method)
        )

    @pytest.fixture
    def spy_binance_margin_client(mocker):
        return mocker.spy(
            execution.exchanges.binance.margin._trading.BinanceMarginTrader, method
        )

    @pytest.fixture
    def mock_binance_futures_client(mocker):
        return mocker.patch.object(
            execution.exchanges.binance.futures._trading.BinanceFuturesTrader, method, getattr(MockBinanceHandler, method)
        )

    @pytest.fixture
    def spy_binance_futures_client(mocker):
        return mocker.spy(
            execution.exchanges.binance.futures._trading.BinanceFuturesTrader, method
        )

    if account_type == 'margin':
        if type_ == 'mock':
            return mock_binance_margin_client

        elif type_ == 'spy':
            return spy_binance_margin_client
    else:
        if type_ == 'mock':
            return mock_binance_futures_client

        elif type_ == 'spy':
            return spy_binance_futures_client


def binance_handler_market_data_factory(method):
    @pytest.fixture
    def mock_binance_handler_market_data(mocker):
        return mocker.patch.object(
            execution.service.blueprints.market_data.BinanceHandler,
            method,
            getattr(MockBinanceHandler, method)
        )

    return mock_binance_handler_market_data


def binance_handler_execution_app_factory(method):
    @pytest.fixture
    def mock_binance_handler(mocker):
        return mocker.patch.object(
            execution.service.app.BinanceFuturesTrader,
            method,
            getattr(MockBinanceHandler, method)
        )

    return mock_binance_handler


def binance_mock_trader_spy_factory(method):
    @pytest.fixture
    def spy_binance_client(mocker):
        return mocker.spy(
            execution.exchanges.binance.margin.mock._trading.BinanceMockMarginTrader, method
        )

    return spy_binance_client


@pytest.fixture
def mocked_futures_create_order(mocker):
    return mocker.patch('execution.exchanges.binance.futures._trading.BinanceFuturesTrader.futures_create_order')
