from datetime import datetime

import pytz
import pytest

from data.tests.helpers.sample_data import exchange_data_1
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
    def create_exchange_data(**kwargs):
        return ExchangeData.objects.create(
            **dict(**exchange_data_1, **kwargs)
        )
    return create_exchange_data


@pytest.fixture
def exchange_data(db, exchange_data_factory):
    return exchange_data_factory()
