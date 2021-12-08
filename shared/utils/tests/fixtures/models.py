import pytest

from data.tests.setup.test_data.sample_data import exchange_data_1
from database.model.models import Exchange, Symbol, ExchangeData, Asset, Jobs, StructuredData, Pipeline

TEST_APP_NAME = 'test_app'


@pytest.fixture
def create_exchange(db):
    return Exchange.objects.create(name='binance')


@pytest.fixture
def create_assets(db):
    obj1 = Asset.objects.create(symbol='BTC')
    obj2 = Asset.objects.create(symbol='USDT')
    obj3 = Asset.objects.create(symbol='BNB')

    return obj1, obj2, obj3


@pytest.fixture
def create_symbol(db, create_assets):
    obj1 = Symbol.objects.create(name='BTCUSDT', base_id='BTC', quote_id='USDT')
    obj2 = Symbol.objects.create(name='BNBBTC', base_id='BNB', quote_id='BTC')
    return obj1, obj2


@pytest.fixture
def create_job(db):
    return Jobs.objects.create(job_id='BTCUSDT', app=TEST_APP_NAME, exchange_id='binance')


@pytest.fixture
def create_pipeline(db, create_exchange, create_symbol):
    return Pipeline.objects.create(
        id=1,
        symbol_id='BTCUSDT',
        strategy='BollingerBands',
        params="{}",
        exchange_id='binance',
        interval="1h",
        active=True
    )


@pytest.fixture
def create_inactive_pipeline(db, create_exchange, create_symbol):
    return Pipeline.objects.create(
        id=3,
        symbol_id='BTCUSDT',
        strategy='Momentum',
        params="{}",
        exchange_id='binance',
        interval="1h",
        active=False
    )


@pytest.fixture
def exchange_data_factory(db, create_exchange, create_symbol):
    def create_exchange_data(**kwargs):
        return ExchangeData.objects.create(**exchange_data_1, **kwargs)
    return create_exchange_data


@pytest.fixture
def exchange_data(db, exchange_data_factory):
    return exchange_data_factory()


@pytest.fixture
def structured_data_factory(db, create_exchange, create_assets, create_symbol):
    def create_structured_data(**kwargs):
        return StructuredData.objects.create(**exchange_data_1, **kwargs)
    return create_structured_data


@pytest.fixture
def structured_data(db, exchange_data_factory):
    return structured_data_factory


@pytest.fixture
def create_structured_data(**kwargs):
    return StructuredData.objects.create(**exchange_data_1, **kwargs)
