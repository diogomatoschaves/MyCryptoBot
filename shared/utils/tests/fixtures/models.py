import datetime
import json
import os
from random import randint

import django
import pytest
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from data.tests.setup.test_data.sample_data import exchange_data_1, exchange_data_2, exchange_data_3
from database.model.models import Exchange, Symbol, ExchangeData, Asset, Jobs, StructuredData, Pipeline, Orders, Trade, \
    Position, Strategy, PortfolioTimeSeries, User

TEST_APP_NAME = 'test_app'


@pytest.fixture
def create_user(db):
    user = User.objects.create(username='username')
    user.set_password('password')
    user.save()


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


def create_strategies(db):
    strategy_1 = Strategy.objects.create(name='MovingAverage', params='{"ma": 4}')
    strategy_2 = Strategy.objects.create(name='Momentum', params='{"window": 6}')

    return strategy_1, strategy_2


def create_invalid_strategy(db):
    return Strategy.objects.create(name='InvalidStrategy', params='{"ma": 4}')

@pytest.fixture
def create_job(db):
    return Jobs.objects.create(job_id='BTCUSDT', app=TEST_APP_NAME, exchange_id='binance')


@pytest.fixture
def create_pipeline(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=1,
        color="purple",
        name='Hello World',
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=True,
        initial_equity=5000,
        leverage=1,
        balance=0,
        units=0.3,
        last_entry=datetime.datetime.now(pytz.utc) - datetime.timedelta(minutes=30)
    )

    pipeline.open_time = datetime.datetime(2023, 10, 1, 16, 0)

    strategy_1, strategy_2 = create_strategies(db)

    pipeline.strategy.add(strategy_1, strategy_2)

    pipeline.save()

    return pipeline


@pytest.fixture
def create_pipeline_2(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=2,
        color="purple",
        name='Hello World',
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=True,
        initial_equity=100,
        leverage=10,
        balance=1000,
        units=0
    )

    pipeline.open_time = datetime.datetime(2023, 10, 1, 16, 0)

    strategy_1, strategy_2 = create_strategies(db)

    pipeline.strategy.add(strategy_1, strategy_2)

    pipeline.save()

    return pipeline


@pytest.fixture
def create_inactive_pipeline(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=3,
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        initial_equity=500,
        active=False,
        balance=1000,
        units=0
    )

    strategy_1, strategy_2 = create_strategies(db)

    pipeline.strategy.add(strategy_1, strategy_2)

    return pipeline


@pytest.fixture
def create_pipeline_with_balance(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=4,
        color="purple",
        name='pipeline with balance',
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=True,
        initial_equity=100,
        leverage=10,
        balance=2000,
        units=-2,
        last_entry=datetime.datetime.now(pytz.utc) - datetime.timedelta(minutes=30)
    )

    strategy_1, strategy_2 = create_strategies(db)

    pipeline.strategy.add(strategy_1, strategy_2)

    return pipeline


@pytest.fixture
def create_pipeline_with_balance_2(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=5,
        color="purple",
        name='pipeline with balance 2',
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=True,
        initial_equity=1000,
        leverage=1,
        balance=1000,
        units=0
    )

    strategy_1, _ = create_strategies(db)

    pipeline.strategy.add(strategy_1)

    return pipeline


@pytest.fixture
def create_pipeline_with_balance_3(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=6,
        color="purple",
        name='pipeline with balance 3',
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=True,
        initial_equity=100,
        leverage=1,
        balance=100,
        units=0
    )

    strategy_1, _ = create_strategies(db)

    pipeline.strategy.add(strategy_1)

    return pipeline


@pytest.fixture
def create_pipeline_with_balance_4(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=12,
        color="purple",
        name='pipeline with balance 4',
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=True,
        initial_equity=100,
        leverage=1,
        balance=2000,
        units=0
    )

    strategy_1, _ = create_strategies(db)

    pipeline.strategy.add(strategy_1)

    return pipeline


@pytest.fixture
def create_pipeline_with_invalid_strategy(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=7,
        color="purple",
        name='pipeline with invalid strategy',
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=True,
        initial_equity=100,
        leverage=1,
        balance=100,
        units=0
    )

    strategy = create_invalid_strategy(db)

    pipeline.strategy.add(strategy)

    return pipeline


@pytest.fixture
def create_deleted_pipeline(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=8,
        color="purple",
        name='deleted pipeline',
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=True,
        initial_equity=100,
        leverage=1,
        balance=100,
        units=0
    )

    strategy_1, _ = create_strategies(db)

    pipeline.strategy.add(strategy_1)

    return pipeline


@pytest.fixture
def create_pipeline_no_equity(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=9,
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        active=False,
        balance=1000,
        units=0
    )

    strategy_1, strategy_2 = create_strategies(db)

    pipeline.strategy.add(strategy_1, strategy_2)

    return pipeline


@pytest.fixture
def create_pipeline_BNBBTC(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=10,
        symbol_id='BNBBTC',
        exchange_id='binance',
        interval="1h",
        initial_equity=500,
        active=True,
        balance=1000,
        units=0
    )

    strategy_1, strategy_2 = create_strategies(db)

    pipeline.strategy.add(strategy_1, strategy_2)

    return pipeline


@pytest.fixture
def create_paper_trading_pipeline(db, create_exchange, create_symbol):
    pipeline = Pipeline.objects.create(
        id=11,
        symbol_id='BTCUSDT',
        exchange_id='binance',
        interval="1h",
        initial_equity=500,
        active=True,
        balance=1000,
        units=0,
        paper_trading=True,
        leverage=4
    )

    strategy_1, strategy_2 = create_strategies(db)

    pipeline.strategy.add(strategy_1, strategy_2)

    return pipeline


@pytest.fixture
def create_all_pipelines(
    db,
    create_pipeline,
    create_pipeline_2,
    create_inactive_pipeline,
    create_pipeline_with_balance,
    create_pipeline_with_balance_2,
    create_pipeline_with_balance_3,
    create_deleted_pipeline
):
    return


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
def create_open_position_paper_trading_pipeline(db, create_paper_trading_pipeline):
    return Position.objects.create(
        position=1,
        symbol_id="BTCUSDT",
        exchange_id='binance',
        pipeline_id=11,
        paper_trading=True,
        buying_price=1000,
        amount=0.1,
        open=True,
    )


@pytest.fixture
def create_neutral_open_inactive_position(db, create_inactive_position, create_open_position, create_neutral_position):
    return


@pytest.fixture
def create_trades(db, create_exchange, create_symbol, create_pipeline, create_pipeline_2):
    trade_1 = Trade.objects.create(
        id=1,
        symbol_id="BTCUSDT",
        open_price=3998.3,
        close_price=4005.2,
        open_time=datetime.datetime(2023, 10, 1, 16, 0),
        close_time=datetime.datetime(2023, 10, 1, 16, 5),
        amount=10,
        side=1,
        exchange_id='binance',
        mock=True,
        pipeline_id=1,
    )

    trade_2 = Trade.objects.create(
        id=2,
        symbol_id="BTCUSDT",
        open_price=4005.2,
        close_price=4002.3,
        open_time=datetime.datetime(2023, 10, 1, 16, 5),
        close_time=datetime.datetime(2023, 10, 1, 16, 10),
        amount=11,
        side=-1,
        exchange_id='binance',
        mock=True,
        pipeline_id=2,
    )

    trade_3 = Trade.objects.create(
        id=3,
        symbol_id="BTCUSDT",
        open_price=4002.3,
        close_price=4010.8,
        open_time=datetime.datetime(2023, 10, 1, 16, 10),
        close_time=datetime.datetime(2023, 10, 1, 16, 15),
        amount=9,
        side=1,
        exchange_id='binance',
        mock=True,
        pipeline_id=2,
    )

    trade_4 = Trade.objects.create(
        id=4,
        symbol_id="BTCUSDT",
        open_price=4002.3,
        open_time=datetime.datetime(2023, 10, 1, 16, 15),
        amount=9,
        side=1,
        exchange_id='binance',
        mock=True,
        pipeline_id=1,
    )

    trade_1.open_time = datetime.datetime(2023, 10, 1, 16, 0)
    trade_2.open_time = datetime.datetime(2023, 10, 1, 16, 5)
    trade_3.open_time = datetime.datetime(2023, 10, 1, 16, 10)

    trade_1.profit_loss = trade_1.get_profit_loss()
    trade_2.profit_loss = trade_2.get_profit_loss()
    trade_3.profit_loss = trade_3.get_profit_loss()

    trade_1.save()
    trade_2.save()
    trade_3.save()

    return trade_1, trade_2, trade_3, trade_4


@pytest.fixture
def create_trades_2(db, create_inactive_pipeline):
    trade_1 = Trade.objects.create(
        id=5,
        symbol_id="BTCUSDT",
        open_price=3998.3,
        close_price=4005.2,
        open_time=datetime.datetime(2023, 10, 1, 16, 0),
        close_time=datetime.datetime(2023, 10, 1, 16, 5),
        amount=10,
        side=1,
        exchange_id='binance',
        mock=True,
        pipeline_id=3,
    )

    trade_2 = Trade.objects.create(
        id=6,
        symbol_id="BNBBTC",
        open_price=3998.3,
        close_price=4005.2,
        open_time=datetime.datetime(2023, 10, 1, 16, 0),
        close_time=datetime.datetime(2023, 10, 1, 16, 5),
        amount=10,
        side=1,
        exchange_id='binance',
        mock=True,
        pipeline_id=9,
    )

    trade_1.open_time = datetime.datetime(2023, 10, 1, 16, 0)
    trade_2.open_time = datetime.datetime(2023, 10, 1, 16, 0)

    trade_1.profit_loss = trade_1.get_profit_loss()
    trade_2.profit_loss = trade_2.get_profit_loss()

    trade_1.save()
    trade_2.save()

    return trade_1, trade_2


@pytest.fixture
def create_pipeline_timeseries(db, create_exchange, create_symbol, create_pipeline):

    entry_1 = PortfolioTimeSeries(
        pipeline_id=1,
        time=datetime.datetime(2023, 10, 1, 10, 0),
        value=1000
    ).save()

    entry_2 = PortfolioTimeSeries(
        pipeline_id=1,
        time=datetime.datetime(2023, 10, 1, 10, 30),
        value=1010
    ).save()

    entry_3 = PortfolioTimeSeries(
        pipeline_id=1,
        time=datetime.datetime(2023, 10, 1, 11, 0),
        value=1020
    ).save()

    entry_4 = PortfolioTimeSeries(
        pipeline_id=1,
        time=datetime.datetime(2023, 10, 1, 11, 30),
        value=1015
    ).save()

    entry_5 = PortfolioTimeSeries(
        pipeline_id=1,
        time=datetime.datetime(2023, 10, 1, 12, 0),
        value=1025
    ).save()

    entry_6 = PortfolioTimeSeries(
        pipeline_id=1,
        time=datetime.datetime(2023, 10, 1, 12, 30),
        value=1030
    ).save()

    entry_7 = PortfolioTimeSeries(
        pipeline_id=1,
        time=datetime.datetime(2023, 10, 1, 10, 0),
        value=1025
    ).save()

    return entry_1, entry_2, entry_3, entry_4, entry_5, entry_6, entry_7


@pytest.fixture
def create_live_portfolio_timeseries(db, create_exchange, create_symbol, create_pipeline):

    entry_1 = PortfolioTimeSeries(
        time=datetime.datetime(2023, 10, 1, 10, 0),
        value=1000,
        type='live'
    ).save()

    entry_2 = PortfolioTimeSeries(
        type='live',
        time=datetime.datetime(2023, 10, 1, 10, 30),
        value=1010
    ).save()

    entry_3 = PortfolioTimeSeries(
        type='live',
        time=datetime.datetime(2023, 10, 1, 11, 0),
        value=1020
    ).save()

    entry_4 = PortfolioTimeSeries(
        type='live',
        time=datetime.datetime(2023, 10, 1, 11, 30),
        value=1015
    ).save()

    entry_5 = PortfolioTimeSeries(
        type='live',
        time=datetime.datetime(2023, 10, 1, 12, 0),
        value=1025
    ).save()

    entry_6 = PortfolioTimeSeries(
        type='live',
        time=datetime.datetime(2023, 10, 1, 12, 30),
        value=1030
    ).save()

    entry_7 = PortfolioTimeSeries(
        type='live',
        time=datetime.datetime(2023, 10, 1, 10, 0),
        value=1025
    ).save()

    return entry_1, entry_2, entry_3, entry_4, entry_5, entry_6, entry_7


@pytest.fixture
def create_testnet_portfolio_timeseries(db, create_pipeline):

    entry_1 = PortfolioTimeSeries(
        time=datetime.datetime(2023, 10, 1, 10, 0),
        value=1000,
        type='testnet'
    ).save()

    entry_2 = PortfolioTimeSeries(
        type='testnet',
        time=datetime.datetime(2023, 10, 1, 10, 30),
        value=1010
    ).save()

    entry_3 = PortfolioTimeSeries(
        type='testnet',
        time=datetime.datetime(2023, 10, 1, 11, 0),
        value=1020
    ).save()

    entry_4 = PortfolioTimeSeries(
        type='testnet',
        time=datetime.datetime(2023, 10, 1, 11, 30),
        value=1015
    ).save()

    entry_5 = PortfolioTimeSeries(
        type='testnet',
        time=datetime.datetime(2023, 10, 1, 12, 0),
        value=1025
    ).save()

    entry_6 = PortfolioTimeSeries(
        type='testnet',
        time=datetime.datetime(2023, 10, 1, 12, 30),
        value=1030
    ).save()

    entry_7 = PortfolioTimeSeries(
        type='testnet',
        time=datetime.datetime(2023, 10, 1, 10, 0),
        value=1025
    ).save()

    return entry_1, entry_2, entry_3, entry_4, entry_5, entry_6, entry_7


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

