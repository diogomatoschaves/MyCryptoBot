import os

import pytest


class MockBinanceTrader:
    def __init__(self, success=True):
        self._success = success

    def start_symbol_trading(self, symbol):
        return self._success

    def stop_symbol_trading(self, symbol):
        return self._success

    def trade(self, symbol, signal, amount):
        pass


@pytest.fixture
def mock_binance_trader_success(mocker):
    return mocker.patch("execution.service.app.binance_trader", MockBinanceTrader())


@pytest.fixture
def mock_binance_trader_fail(mocker):
    return mocker.patch(
        "execution.service.app.binance_trader", MockBinanceTrader(success=False)
    )
