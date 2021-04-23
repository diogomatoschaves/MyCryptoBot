import time

import pytest
import requests
from binance.client import Client
from rq.exceptions import NoSuchJobError

import model
from data.tests.setup.test_data.sample_data import binance_api_historical_data
from shared.exchanges import BinanceHandler

response = {"response": "Something", "success": True}


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


def mock_response(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.ok = True

        def json(self):
            return self.json_data

        @property
        def text(self):
            return response["response"]

    return MockResponse(response, 200)


@pytest.fixture
def mock_requests_post(mocker):
    return mocker.patch.object(requests, "post", mock_response)


@pytest.fixture
def requests_post_spy(mocker):
    return mocker.spy(requests, "post")


@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch.object(requests, "get", mock_response)


@pytest.fixture
def requests_get_spy(mocker):
    return mocker.spy(requests, "get")


@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch.object(time, "sleep", lambda seconds: None)


def mock_rq_job(*args, **kwargs):
    class MockJob:
        def __init__(self):
            for kwarg, value in kwargs.items():
                setattr(self, kwarg, value)

            if "raise_error" in kwargs:
                raise NoSuchJobError

    return MockJob()


@pytest.fixture
def mocked_rq_job(mocker):
    return mocker.patch('rq.job.Job.fetch')


def mock_enqueue_call(get_signal, params):
    class MockJob:
        def __init__(self):
            pass

        def get_id(self):
            return 'abcde'

    return MockJob()


@pytest.fixture
def mocked_rq_enqueue_call(mocker):
    return mocker.patch.object(model.service.app.q, 'enqueue_call', mock_enqueue_call)