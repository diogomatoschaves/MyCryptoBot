import os

import pytest

import model
from model.tests.setup.test_data.sample_data import STRATEGIES

TEST_APP_NAME = "test_app"
EXECUTION_APP_URL = "https://example.com"


@pytest.fixture()
def mock_settings_env_vars(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "APP_NAME": TEST_APP_NAME,
            "EXECUTION_APP_URL": EXECUTION_APP_URL,
        },
    )


@pytest.fixture()
def mock_get_data(mocker):
    return mocker.patch("model.service.helpers.signal_generator.get_data")


@pytest.fixture()
def mock_trigger_order(mocker):
    return mocker.patch("model.service.helpers.signal_generator.trigger_order")


@pytest.fixture()
def mock_execute_order(mocker):
    return mocker.patch("model.service.helpers.signal_generator.execute_order")


def mock_strategy(*args, **kwargs):
    class MockStrategy:
        def __init__(self, *args1, **kwargs1):
            pass

        def get_signal(self):
            return 1

    return MockStrategy()


def mock_strategy_factory(strategy):
    @pytest.fixture()
    def mocked_strategy(mocker):
        mocker.patch.object(model.service.helpers.signal_generator, strategy, mock_strategy)

    return mocked_strategy


@pytest.fixture()
def mocked_strategy_combiner(mocker):
    mocker.patch.object(model.service.helpers.signal_generator, 'StrategyCombiner', mock_strategy)


def mock_redis():
    class RedisCache:

        def __init__(self):
            print("Redis initialized")

        def set(self, object_name, object_value):
            setattr(self, object_name, object_value)

        def get(self, object_name):
            try:
                return getattr(self, object_name)
            except AttributeError:
                '""'

    return RedisCache()


@pytest.fixture
def mock_redis_connection(mocker):
    return mocker.patch("model.service.app.cache", mock_redis())


@pytest.fixture
def mock_strategies(mocker):
    mocker.patch.object(model.service.app, "STRATEGIES", STRATEGIES)
