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


def binance_client_mock_factory(method, type_='mock'):

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


@pytest.fixture
def mocked_futures_create_order(mocker):
    return mocker.patch('execution.exchanges.binance.futures._trading.BinanceFuturesTrader.futures_create_order')
