import datetime
import os
from random import randint

import django
import pytest
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from data.tests.setup.test_data.sample_data import exchange_data_1, exchange_data_2, exchange_data_3
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
    obj1 = Symbol.objects.create(name='BTCUSDT', base_id='BTC', quote_id='USDT', price_precision=2, quantity_precision=3)
    obj2 = Symbol.objects.create(name='BNBBTC', base_id='BNB', quote_id='BTC', price_precision=2, quantity_precision=3)
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
        equity=100,
        leverage=1,
        balance=1000,
        units=0
    )


@pytest.fixture
def create_pipeline_2(db, create_exchange, create_symbol):
    return Pipeline.objects.create(
        id=2,
        color="purple",
        name='Hello World',
        symbol_id='BTCUSDT',
        strategy='MovingAverage',
        params='{"ma": 30}',
        exchange_id='binance',
        interval="1h",
        active=True,
        equity=100,
        leverage=10,
        balance=1000,
        units=0
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
        active=False,
        balance=1000,
        units=0
    )


@pytest.fixture
def create_pipeline_with_balance(db, create_exchange, create_symbol):
    return Pipeline.objects.create(
        id=4,
        color="purple",
        name='pipeline with balance',
        symbol_id='BTCUSDT',
        strategy='MovingAverage',
        params='{"ma": 30}',
        exchange_id='binance',
        interval="1h",
        active=True,
        equity=100,
        leverage=1,
        balance=2000,
        units=-2
    )


@pytest.fixture
def create_pipeline_with_balance_2(db, create_exchange, create_symbol):
    return Pipeline.objects.create(
        id=5,
        color="purple",
        name='pipeline with balance 2',
        symbol_id='BTCUSDT',
        strategy='MovingAverage',
        params='{"ma": 30}',
        exchange_id='binance',
        interval="1h",
        active=True,
        equity=1000,
        leverage=1,
        balance=1000,
        units=0
    )


@pytest.fixture
def create_pipeline_with_balance_3(db, create_exchange, create_symbol):
    return Pipeline.objects.create(
        id=6,
        color="purple",
        name='pipeline with balance 3',
        symbol_id='BTCUSDT',
        strategy='MovingAverage',
        params='{"ma": 30}',
        exchange_id='binance',
        interval="1h",
        active=True,
        equity=100,
        leverage=1,
        balance=100,
        units=0
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
def create_neutral_position(db, create_pipeline):
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
def create_open_position(db, create_pipeline_2):
    return Position.objects.create(
        position=1,
        symbol_id="BTCUSDT",
        exchange_id='binance',
        pipeline_id=2,
        paper_trading=True,
        buying_price=1000,
        amount=0.1,
        open=True,
    )


@pytest.fixture
def create_inactive_position(db, create_inactive_pipeline):
    return Position.objects.create(
        position=1,
        symbol_id="BTCUSDT",
        exchange_id='binance',
        pipeline_id=3,
        paper_trading=True,
        buying_price=10000,
        amount=0.1,
        open=True,
    )


@pytest.fixture
def create_neutral_open_inactive_position(db, create_inactive_position, create_open_position, create_neutral_position):
    return


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
        obj_1 = StructuredData.objects.create(**exchange_data_1, **kwargs)
        obj_2 = StructuredData.objects.create(**exchange_data_2, **kwargs)
        return obj_1, obj_2

    return create_structured_data


@pytest.fixture
def structured_data(db, exchange_data_factory):
    obj_1, obj_2 = structured_data_factory
    return obj_1, obj_2


@pytest.fixture
def create_structured_data(**kwargs):
    return StructuredData.objects.create(**exchange_data_1, **kwargs)


@pytest.fixture
def populate_exchange_data(db, create_symbol, create_exchange):
    entry_1 = ExchangeData.objects.create(**exchange_data_1)
    entry_2 = ExchangeData.objects.create(**exchange_data_2)
    entry_3 = ExchangeData.objects.create(**exchange_data_3)
    return entry_1, entry_2, entry_3


@pytest.fixture
def populate_structured_data(db, create_symbol, create_exchange):
    entry_1 = StructuredData.objects.create(**exchange_data_1)
    entry_2 = StructuredData.objects.create(**exchange_data_2)
    # entry_3 = StructuredData.objects.create(**exchange_data_3)
    return entry_1

