from datetime import datetime

import pytz
import pytest

from database.model.models import Exchange, Symbol, ExchangeData


@pytest.fixture
def create_exchange(db):
    return Exchange.objects.create(name='binance')


@pytest.fixture
def create_symbol(db):
    return Symbol.objects.create(name='BTCUSDT')


@pytest.fixture
def exchange_data_factory(db, create_exchange, create_symbol):
    # Closure
    def create_exchange_data(
        open_time=datetime(2019, 9, 2, 10, tzinfo=pytz.utc),
        close_time=datetime(2019, 9, 1, 11, tzinfo=pytz.utc)
    ):
        return ExchangeData.objects.create(
            exchange=create_exchange,
            symbol=create_symbol,
            open_time=open_time,
            close_time=close_time,
            interval='1h',
            open=1000,
            high=1010,
            low=990,
            close=1005,
            volume=10,
            quote_volume=1E4,
            trades=2,
            taker_buy_asset_volume=5,
            taker_buy_quote_volume=5E3,
        )
    return create_exchange_data


@pytest.fixture
def exchange_data(db, exchange_data_factory):
    return exchange_data_factory()
