import os

import pytest

import model


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
    return mocker.patch("model.strategies.signal_generator.get_data")


@pytest.fixture()
def mock_trigger_order(mocker):
    return mocker.patch("model.strategies.signal_generator.trigger_order")


@pytest.fixture()
def mock_execute_order(mocker):
    return mocker.patch("model.strategies.signal_generator.execute_order")


def mock_strategy(*args, **kwargs):
    class MockStrategy:
        def __init__(self, *args1, **kwargs1):
            pass

        def get_signal(self):
            return 1

    return MockStrategy()


def mock_strategy_factory(strategy):
    def mock_strategy(*args, **kwargs):
        class MockStrategy:
            def __init__(self, *args1, **kwargs1):
                pass

            def get_signal(self):
                return 1

        return MockStrategy()

    @pytest.fixture()
    def mocked_strategy(mocker):
        mocker.patch.object(model.strategies.signal_generator, strategy, mock_strategy)

    return mocked_strategy
