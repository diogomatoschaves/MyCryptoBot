import os

import pytest

from execution.service import create_app
import execution


TEST_APP_NAME = "test_app"


def mock_init(x=None, **kwargs):
    pass


@pytest.fixture
def futures_init_session(mocker):
    return mocker.patch.object(
        execution.service.app.BinanceFuturesTrader, "_init_session", mock_init
    )


@pytest.fixture
def margin_init_session(mocker):
    return mocker.patch.object(
        execution.service.app.BinanceMarginTrader, "_init_session", mock_init
    )


@pytest.fixture
def futures_init(mocker, futures_init_session):
    return mocker.patch.object(
        execution.service.app.BinanceFuturesTrader, "ping", mock_init
    )


@pytest.fixture
def margin_init(mocker, margin_init_session):
    return mocker.patch.object(
        execution.service.app.BinanceMarginTrader, "ping", mock_init
    )


@pytest.fixture()
def mock_client_env_vars(mocker):
    mocker.patch.dict(os.environ, {"APP_NAME": TEST_APP_NAME})


@pytest.fixture
def app(mock_client_env_vars, futures_init, margin_init):
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
