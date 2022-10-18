import os

import pytest
from binance.exceptions import BinanceAPIException


class MockBinanceTrader:
    def __init__(self, success=True, raise_error_trade=False, raise_error_start_stop=False):
        self._success = success
        self.raise_error_trade = raise_error_trade
        self.raise_error_start_stop = raise_error_start_stop

    def start_symbol_trading(self, symbol, header='', **kwargs):
        if self.raise_error_start_stop:
            print("gonna raise that exception")
            raise BinanceAPIException(
                '',
                400,
                '{"msg": "ReduceOnly Order is rejected.", "code": -2022}'
            )
        return self._success

    def stop_symbol_trading(self, symbol, header='', **kwargs):
        if self.raise_error_start_stop:
            print("gonna raise that exception")
            raise BinanceAPIException(
                '',
                400,
                '{"msg": "ReduceOnly Order is rejected.", "code": -2022}'
            )
        return self._success

    def trade(self, symbol, signal, amount, header='', **kwargs):
        if self.raise_error_trade:
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
def mock_binance_futures_trader_raise_exception_trade(mocker):
    return mocker.patch("execution.service.app.binance_futures_trader", MockBinanceTrader(raise_error_trade=True))


@pytest.fixture
def mock_binance_futures_trader_raise_exception_start_stop(mocker):
    return mocker.patch("execution.service.app.binance_futures_trader", MockBinanceTrader(raise_error_start_stop=True))



