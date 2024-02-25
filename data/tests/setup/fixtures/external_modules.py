import datetime

import flask_jwt_extended
import pytest
import redis
from binance import ThreadedWebsocketManager
from binance.client import Client
from django import db

import data
from data.tests.setup.test_data.binance_api_responses import exchange_info
from data.tests.setup.test_data.sample_data import binance_api_historical_data
from shared.exchanges.binance import BinanceHandler


def mock_get_historical_klines_generator(symbol, candle_size, start_date, end_date, limit):
    return binance_api_historical_data


def mock_client_init_session(self):
    return None


@pytest.fixture
def mock_binance_handler_klines(mocker):
    mocker.patch.object(
        BinanceHandler,
        "get_historical_klines",
        lambda self, symbol, candle_size, start_date, end_date, limit:
            mock_get_historical_klines_generator(symbol, candle_size, start_date, end_date, limit)
    )


@pytest.fixture
def spy_binance_handler_klines(mocker):
    return mocker.spy(BinanceHandler, "get_historical_klines")


@pytest.fixture
def mock_binance_client_init(mocker):
    mocker.patch.object(Client, "_init_session", lambda self: None)


@pytest.fixture
def mock_binance_client_ping(mocker):
    mocker.patch.object(Client, "ping", lambda self: None)


@pytest.fixture
def mock_binance_threaded_websocket(mocker):
    mocker.patch.object(ThreadedWebsocketManager, "__init__", lambda self, api_key, api_secret: None)


@pytest.fixture
def mock_binance_client_exchange_info(mocker):
    mocker.patch.object(Client, "futures_exchange_info", lambda self: exchange_info)


def create_access_token(x=None, **kwargs):
    return "abc"


@pytest.fixture
def mock_create_access_token(mocker):
    return mocker.patch("data.service.app.create_access_token", create_access_token)


@pytest.fixture
def mock_create_access_token_user_mgmt(mocker):
    return mocker.patch.object(
        data.service.blueprints.user_management,
        'create_access_token',
        lambda identity: 'access_token' if identity is not None else 'renewed_access_token'
    )


@pytest.fixture
def spy_db_connection(mocker):
    return mocker.spy(db.connections, 'all')


FAKE_TIME = datetime.datetime(2023, 11, 1, )


@pytest.fixture
def patch_datetime_now(monkeypatch):

    class mydatetime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return FAKE_TIME

    monkeypatch.setattr(datetime, 'datetime', mydatetime)
