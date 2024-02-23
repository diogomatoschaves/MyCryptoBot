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
    return mocker.patch("model.signal_generation._signal_generation.get_data")


@pytest.fixture()
def mock_trigger_order(mocker):
    return mocker.patch("model.signal_generation._signal_generation.trigger_order")


@pytest.fixture()
def mock_execute_order(mocker):
    return mocker.patch("model.signal_generation._signal_generation.execute_order")


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
        mocker.patch.object(model.signal_generation._signal_generation, strategy, mock_strategy)

    return mocked_strategy


@pytest.fixture()
def mocked_strategy_combiner(mocker):
    mocker.patch.object(model.signal_generation._signal_generation, 'StrategyCombiner', mock_strategy)


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
def mock_compile_strategies(mocker):
    mocker.patch.object(model.service.app, 'compile_strategies', lambda: STRATEGIES)


@pytest.fixture
def spy_upload_file(mocker):
    return mocker.spy(model.service.cloud_storage._cloud_storage, "upload_file")


@pytest.fixture
def spy_download_file(mocker):
    return mocker.spy(model.service.cloud_storage._cloud_storage, "download_file")


@pytest.fixture
def mock_local_models_storage(mocker, tmp_path):
    return mocker.patch(
        "model.signal_generation._signal_generation.LOCAL_MODELS_LOCATION",
        tmp_path
    )


@pytest.fixture
def create_mock_file(tmp_path):
    with open(os.path.join(tmp_path, 'mock-file.pkl'), 'w') as f:
        f.write("Mock")
