import os

import pytest

import data
from data.service import create_app
from data.sources.binance import BinanceDataHandler
from database.model.models import Exchange, Symbol, Asset, Jobs


TEST_APP_NAME = 'test_app'


@pytest.fixture()
def mock_settings_env_vars(mocker):
    mocker.patch.dict(os.environ, {"APP_NAME": TEST_APP_NAME})


@pytest.fixture
def mock_start_stop_symbol_trading_success_true(mocker):
    mocker.patch.object(
        data.service.app,
        'start_stop_symbol_trading',
        lambda symbol, exchange, start_or_stop: {"success": True, "response": ''},
    )


@pytest.fixture
def mock_start_stop_symbol_trading_success_false(mocker):
    return mocker.patch.object(
        data.service.app,
        'start_stop_symbol_trading',
        lambda symbol, exchange, start_or_stop: {"success": False, "response": 'Failed'},
    )


@pytest.fixture
def app(mock_settings_env_vars):
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def client_success_external_call(app_success_external_call):
    """A test client for the app."""
    with app_success_external_call.test_client() as client:
        yield client


@pytest.fixture
def create_exchange(db):
    return Exchange.objects.create(name='binance')


@pytest.fixture
def create_assets(db):
    obj1 = Asset.objects.create(symbol='BTC')
    obj2 = Asset.objects.create(symbol='USDT')

    return [obj1, obj2]


@pytest.fixture
def create_symbol():
    return Symbol.objects.create(name='BTCUSDT', base_id='BTC', quote_id='USDT')


@pytest.fixture
def create_job(db):
    return Jobs.objects.create(job_id='BTCUSDT', app=TEST_APP_NAME, exchange_id='binance')


@pytest.fixture
def mock_binance_handler_start_data_ingestion(mocker):
    mocker.patch.object(
        BinanceDataHandler,
        "start_data_ingestion",
        lambda self: None
    )


@pytest.fixture
def mock_binance_handler_stop_data_ingestion(mocker):
    return mocker.patch.object(
        BinanceDataHandler,
        "stop_data_ingestion",
        lambda self: None
    )


@pytest.fixture
def binance_handler_stop_data_ingestion_spy(mocker):
    return mocker.spy(BinanceDataHandler, 'stop_data_ingestion')


@pytest.fixture
def binance_handler_instances_spy_start_bot(mocker):
    return mocker.patch('data.service.app.binance_instances', new_callable=list)


def immediate_execution(initialize_data_collection, strategy, params, symbol, candle_size):
    return initialize_data_collection(strategy, params, symbol, candle_size)


@pytest.fixture
def mock_executor_submit(mocker):
    mocker.patch.object(
        data.service.app.executor,
        "submit",
        immediate_execution
    )


@pytest.fixture
def binance_handler_instances_spy_stop_bot(db, create_symbol, create_assets, create_exchange, mocker):
    return mocker.patch(
        'data.service.app.binance_instances',
        [BinanceDataHandler("MovingAverageCrossover", symbol='BTCUSDT')]
    )


@pytest.fixture
def binance_handler_instances_spy(mocker):
    return mocker.spy(data.service.app, 'binance_instances')
