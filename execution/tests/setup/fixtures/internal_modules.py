import os

import pytest
from binance.exceptions import BinanceAPIException


class MockBinanceTrader:
    def __init__(self, success=True, raise_trade_error=False):
        self._success = success
        self.raise_trade_error = raise_trade_error

    def start_symbol_trading(self, symbol, header='', **kwargs):
        return self._success

    def stop_symbol_trading(self, symbol, header='', **kwargs):
        return self._success

    def trade(self, symbol, signal, amount, header='', **kwargs):
        if self.raise_trade_error:
            raise BinanceAPIException(
                '',
                400,
                '{"msg": "Precision is over the maximum defined for this asset.", "code": -1111}'
            )


@pytest.fixture
def mock_binance_margin_trader_success(mocker):
    return mocker.patch("execution.service.app.binance_margin_trader", MockBinanceTrader())


@pytest.fixture
def mock_binance_margin_trader_fail(mocker):
    return mocker.patch(
        "execution.service.app.binance_margin_trader", MockBinanceTrader(success=False)
    )

@pytest.fixture
def mock_binance_futures_trader_success(mocker):
    return mocker.patch("execution.service.app.binance_futures_trader", MockBinanceTrader())


@pytest.fixture
def mock_binance_futures_trader_fail(mocker):
    return mocker.patch(
        "execution.service.app.binance_futures_trader", MockBinanceTrader(success=False)
    )


def mock_redis():
    class RedisCache:

        def __init__(self):
            print("Redis initialized")

        def set(self, object_name, object_value):
            setattr(self, object_name, object_value)

        def get(self, object_name):
            try:
                return getattr(self, object_name)
            except AttributeError:
                '""'

    return RedisCache()


@pytest.fixture
def mock_redis_connection(mocker):
    return mocker.patch("execution.service.helpers._helpers.cache", mock_redis())


@pytest.fixture
def mock_binance_futures_trader_trade_exception(mocker):
    return mocker.patch("execution.service.app.binance_futures_trader", MockBinanceTrader(raise_trade_error=True))
