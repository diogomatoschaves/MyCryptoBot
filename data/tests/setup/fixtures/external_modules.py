import pytest
import redis
from binance.client import Client

from data.tests.setup.test_data.sample_data import binance_api_historical_data
from shared.exchanges import BinanceHandler


def mock_get_historical_klines_generator(symbol, candle_size, start_date):
    for kline in binance_api_historical_data:
        yield kline


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
def mock_binance_client_init(mocker):
    mocker.patch.object(Client, "_init_session", lambda self: None)


@pytest.fixture
def mock_binance_client_ping(mocker):
    mocker.patch.object(Client, "ping", lambda self: None)
