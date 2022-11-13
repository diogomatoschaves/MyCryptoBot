import datetime
import os
from random import randint

import django
import pytest
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from data.tests.setup.test_data.sample_data import exchange_data_1
from database.model.models import Exchange, Symbol, ExchangeData, Asset, Jobs, StructuredData, Pipeline, Orders, Trade, \
    Position

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
        color="purple",
        name='Hello World',
        symbol_id='BTCUSDT',
        strategy='MovingAverage',
        params='{"ma": 30}',
        exchange_id='binance',
        interval="1h",
        active=True,
        allocation=100,
        leverage=1
    )


@pytest.fixture
def create_orders(db, create_exchange, create_symbol, create_pipeline):
    order_1 = Orders.objects.create(
        order_id=randint(1, 1E9),
        client_order_id=1234,
        symbol_id="BTCUSDT",
        transact_time=datetime.datetime.now(pytz.utc),
        price=3998.3,
        original_qty=10,
        executed_qty=10,
        cummulative_quote_qty=0,
        status="FILLED",
        type="MARKET",
        side="BUY",
        is_isolated=True,
        mock=True,
        pipeline_id=1
    )
    order_2 = Orders.objects.create(
        order_id=randint(1, 1E9),
        client_order_id=1234,
        symbol_id="BTCUSDT",
        transact_time=datetime.datetime.now(pytz.utc),
        price=3998.3,
        original_qty=10,
        executed_qty=10,
        cummulative_quote_qty=0,
        status="FILLED",
        type="MARKET",
        side="BUY",
        is_isolated=True,
        mock=True,
        pipeline_id=1
    )
    return order_1, order_2


@pytest.fixture
def create_position(db, create_exchange, create_symbol, create_pipeline):
    return Position.objects.create(
        position=0,
        symbol_id="BTCUSDT",
        exchange_id='binance',
        pipeline_id=1,
        paper_trading=True,
        buying_price=0,
        amount=0,
        open=False,
    )


@pytest.fixture
def create_trade(db, create_exchange, create_symbol, create_pipeline):
    return Trade.objects.create(
        symbol_id="BTCUSDT",
        open_price=3998.3,
        amount=10,
        side=-1,
        exchange_id='binance',
        mock=True,
        pipeline_id=1,
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
