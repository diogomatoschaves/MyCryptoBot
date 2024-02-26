import os

import pytest

from execution.service import create_app
from execution.tests.setup.fixtures.internal_modules import *
from execution.tests.setup.fixtures.external_modules import *
import execution


TEST_APP_NAME = "test_app"


@pytest.fixture
def futures_init_session(mocker):
    return mocker.patch.object(
        execution.service.app.BinanceFuturesTrader, "_init_session", lambda x=None, **kwargs: None
    )


@pytest.fixture
def futures_init(mocker, futures_init_session):
    return mocker.patch.object(
        execution.service.app.BinanceFuturesTrader, "ping", lambda x=None, **kwargs: None
    )


@pytest.fixture()
def mock_client_env_vars(mocker):
    mocker.patch.dict(os.environ, {"APP_NAME": TEST_APP_NAME})


@pytest.fixture
def app(
    mock_client_env_vars,
    futures_init,
    mock_jwt_required,
    mock_redis_connection,
    exchange_data,
    create_pipeline,
    create_inactive_pipeline,
):
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
