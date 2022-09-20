import os

import pytest


class MockBinanceTrader:
    def __init__(self, success=True):
        self._success = success

    def start_symbol_trading(self, symbol, header='', **kwargs):
        return self._success

    def stop_symbol_trading(self, symbol, header='', **kwargs):
        return self._success

    def trade(self, symbol, signal, amount, header='', **kwargs):
        pass


@pytest.fixture
def mock_binance_trader_success(mocker):
    return mocker.patch("execution.service.app.binance_margin_trader", MockBinanceTrader())


@pytest.fixture
def mock_binance_trader_fail(mocker):
    return mocker.patch(
        "execution.service.app.binance_margin_trader", MockBinanceTrader(success=False)
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
