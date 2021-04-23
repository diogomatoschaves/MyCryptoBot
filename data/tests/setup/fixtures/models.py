import pytest

from data.tests.setup.test_data.sample_data import exchange_data_1
from database.model.models import Exchange, Symbol, ExchangeData, Asset, Jobs


TEST_APP_NAME = 'test_app'


@pytest.fixture
def create_exchange(db):
    return Exchange.objects.create(name='binance')


@pytest.fixture
def create_assets(db):
    obj1 = Asset.objects.create(symbol='BTC')
    obj2 = Asset.objects.create(symbol='USDT')

    return [obj1, obj2]


@pytest.fixture
def create_symbol(db):
    return Symbol.objects.create(name='BTCUSDT', base_id='BTC', quote_id='USDT')


@pytest.fixture
def create_job(db):
    return Jobs.objects.create(job_id='BTCUSDT', app=TEST_APP_NAME, exchange_id='binance')


@pytest.fixture
def exchange_data_factory(db, create_exchange, create_assets, create_symbol):
    def create_exchange_data(**kwargs):
        return ExchangeData.objects.create(**exchange_data_1, **kwargs)
    return create_exchange_data


@pytest.fixture
def exchange_data(db, exchange_data_factory):
    return exchange_data_factory()
