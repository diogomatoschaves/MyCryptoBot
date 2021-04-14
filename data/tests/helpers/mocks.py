import pytest

from binance.client import Client

from data.tests.helpers.sample_data import binance_api_historical_data
from shared.exchanges.binance import BinanceHandler


def mock_get_historical_klines_generator(symbol, candle_size, start_date):
    return binance_api_historical_data


def mock_start_multiplex_socket(self, streams, callback):
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
    mocker.patch.object(BinanceHandler, "start_multiplex_socket", mock_start_multiplex_socket)


@pytest.fixture
def mock_binance_client_init(mocker):
    mocker.patch.object(Client, "_init_session", lambda self: None)


@pytest.fixture
def mock_binance_client_ping(mocker):
    mocker.patch.object(Client, "ping", lambda self: None)

