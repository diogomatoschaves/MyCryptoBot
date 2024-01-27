import os

import pytest
from binance.exceptions import BinanceAPIException

import execution
from execution.service.helpers.exceptions import SymbolNotBeingTraded, SymbolAlreadyTraded, LeverageSettingFail, \
    NegativeEquity


class MockBinanceTrader:
    def __init__(
        self,
        raise_error_trade=False,
        raise_error_start_stop=False,
        raise_symbol_not_being_traded=False,
        raise_symbol_already_traded=False,
        raise_leverage_setting_failure=False,
        raise_negative_equity_error=False
    ):
        self.raise_error_trade = raise_error_trade
        self.raise_error_start_stop = raise_error_start_stop
        self.raise_symbol_not_being_traded = raise_symbol_not_being_traded
        self.raise_symbol_already_traded = raise_symbol_already_traded
        self.raise_leverage_setting_failure = raise_leverage_setting_failure
        self.raise_negative_equity_error = raise_negative_equity_error

    def start_symbol_trading(self, symbol, current_equity, pipeline_id, header='', **kwargs):

        if self.raise_error_start_stop:
            raise BinanceAPIException(
                '',
                400,
                '{"msg": "ReduceOnly Order is rejected.", "code": -2022}'
            )
        elif self.raise_symbol_already_traded:
            raise SymbolAlreadyTraded(symbol)
        elif self.raise_leverage_setting_failure:
            raise LeverageSettingFail("")

    def stop_symbol_trading(self, symbol, header='', **kwargs):
        if self.raise_error_start_stop:
            raise BinanceAPIException(
                '',
                400,
                '{"msg": "ReduceOnly Order is rejected.", "code": -2022}'
            )
        if self.raise_symbol_not_being_traded:
            raise SymbolNotBeingTraded(symbol)

    def trade(self, symbol, signal, amount, header='', **kwargs):
        if self.raise_error_trade:
            raise BinanceAPIException(
                '',
                400,
                '{"msg": "Precision is over the maximum defined for this asset.", "code": -1111}'
            )
        elif self.raise_negative_equity_error:
            raise NegativeEquity(1)


@pytest.fixture
def mock_binance_margin_trader_success(mocker):
    return mocker.patch("execution.service.app.binance_margin_trader", MockBinanceTrader())


@pytest.fixture
def mock_binance_futures_trader_success(mocker):
    return mocker.patch("execution.service.app.binance_futures_trader", MockBinanceTrader())


@pytest.fixture
def mock_binance_margin_trader_fail(mocker):
    return mocker.patch(
        "execution.service.app.binance_margin_trader",
        MockBinanceTrader(raise_symbol_not_being_traded=True, raise_symbol_already_traded=True),
    )


@pytest.fixture
def mock_binance_margin_trader_fail_pipeline_inactive(mocker):
    return mocker.patch(
        "execution.service.app.binance_margin_trader",
        MockBinanceTrader(),
    )


@pytest.fixture
def mock_binance_futures_trader_fail(mocker):
    return mocker.patch(
        "execution.service.app.binance_futures_trader",
        MockBinanceTrader(raise_symbol_not_being_traded=True, raise_symbol_already_traded=True),
    )


@pytest.fixture
def mock_binance_futures_trader_fail_pipeline_inactive(mocker):
    return mocker.patch(
        "execution.service.app.binance_futures_trader",
        MockBinanceTrader(),
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
def mock_binance_futures_trader_raise_negative_equity_error(mocker):
    return mocker.patch("execution.service.app.binance_futures_trader", MockBinanceTrader(raise_negative_equity_error=True))


@pytest.fixture
def mock_binance_futures_trader_raise_exception_start_stop(mocker):
    return mocker.patch("execution.service.app.binance_futures_trader", MockBinanceTrader(raise_error_start_stop=True))


@pytest.fixture
def mock_binance_futures_trader_raise_leverage_setting_fail(mocker):
    return mocker.patch("execution.service.app.binance_futures_trader", MockBinanceTrader(raise_leverage_setting_failure=True))


@pytest.fixture
def mock_start_pipeline_trade(mocker):
    return mocker.patch.object(
        execution.service.app,
        "start_pipeline_trade",
        lambda pipeline, binance_account_type, header, **kwargs: None
    )


@pytest.fixture
def spy_start_pipeline_trade(mocker):
    return mocker.spy(execution.service.app, "start_pipeline_trade")


@pytest.fixture
def mock_futures_symbol_ticker(mocker):
    return mocker.patch.object(
        execution.service.cron_jobs.save_pipelines_snapshot._save_pipelines_snapshot,
        'get_ticker',
        lambda symbol: {"price": 1000}
    )
