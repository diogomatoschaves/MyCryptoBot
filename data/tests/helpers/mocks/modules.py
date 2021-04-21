import pytest

from binance.client import Client

import data
from data.sources.binance import BinanceDataHandler
from data.tests.helpers.sample_data import mock_websocket_raw_data_1h, \
    mock_websocket_raw_data_5m, binance_api_historical_data
from data.tests.helpers.mocks.models import *
from shared.exchanges.binance import BinanceHandler


def mock_get_historical_klines_generator(symbol, candle_size, start_date):
    for kline in binance_api_historical_data:
        yield kline


def double_callback(callback, mock_row):
    callback(mock_row[0])
    callback(mock_row[1])


def mock_start_multiplex_socket(self, streams, callback):
    double_callback(callback, mock_websocket_raw_data_5m)
    double_callback(callback, mock_websocket_raw_data_1h)

    return f"streams={'/'.join(streams)}"


def mock_client_init_session(self):
    return None


@pytest.fixture
def mock_binance_handler_klines(mocker):
    mocker.patch.object(
        BinanceHandler,
        "get_historical_klines_generator",
        lambda self, symbol, candle_size, stat_date: mock_get_historical_klines_generator(symbol, candle_size, stat_date)
    )


@pytest.fixture
def mock_binance_handler_websocket(mocker):
    mocker.patch.object(BinanceDataHandler, "start_multiplex_socket", mock_start_multiplex_socket)


@pytest.fixture
def mock_binance_websocket_start(mocker):
    mocker.patch.object(BinanceDataHandler, "start", lambda self: None)


@pytest.fixture
def mock_binance_client_init(mocker):
    mocker.patch.object(Client, "_init_session", lambda self: None)


@pytest.fixture
def mock_binance_client_ping(mocker):
    mocker.patch.object(Client, "ping", lambda self: None)


@pytest.fixture
def mock_trigger_signal_successfully(mocker):
    return mocker.patch.object(
        data.sources.binance._binance,
        'trigger_signal',
        lambda symbol, strategy, params, candle_size, exchange: True,
        # wraps=data.sources.binance._binance.trigger_signal
    )


@pytest.fixture
def mock_trigger_signal_fail(mocker):
    mocker.patch.object(
        data.sources.binance._binance,
        'trigger_signal',
        lambda symbol, strategy, params, candle_size, exchange: False,
        wraps=data.sources.binance._binance.trigger_signal
    )


@pytest.fixture
def trigger_signal_spy(mocker):
    return mocker.spy(data.sources.binance._binance, 'trigger_signal')
