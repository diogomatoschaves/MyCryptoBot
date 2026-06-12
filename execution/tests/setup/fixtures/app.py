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
def mock_startup_task(mocker):
    """Endpoint-focused tests boot the app without the startup side effects
    (scheduler, reconciliation, auto-starting active pipelines)."""
    return mocker.patch("execution.service.app.startup_task")


@pytest.fixture
def mock_reconcile_positions(mocker):
    """Startup-focused tests run the real startup_task but skip the exchange
    reconciliation, which would otherwise attempt network calls."""
    return mocker.patch("execution.service.app.reconcile_positions")


@pytest.fixture
def app(
    mock_client_env_vars,
    futures_init,
    mock_jwt_required,
    mock_redis_connection,
    exchange_data,
    create_pipeline,
    create_inactive_pipeline,
    mock_startup_task,
):
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_with_open_positions(
    mock_client_env_vars,
    futures_init,
    mock_jwt_required,
    mock_redis_connection,
    exchange_data,
    create_positions,
    mock_reconcile_positions,
    mock_start_pipeline_trade,
    spy_start_pipeline_trade
):
    app = create_app(testing=True)
    return app


@pytest.fixture
def app_with_open_positions_insufficient_balance(
    mock_client_env_vars,
    futures_init,
    mock_jwt_required,
    mock_redis_connection,
    exchange_data,
    create_positions,
    mock_reconcile_positions,
    mock_start_pipeline_trade_raise_exception,
    spy_start_pipeline_trade
):
    app = create_app(testing=True)
    return app


@pytest.fixture
def app_with_open_positions_generic_error(
    mock_client_env_vars,
    futures_init,
    mock_jwt_required,
    mock_redis_connection,
    exchange_data,
    create_positions,
    mock_reconcile_positions,
    mock_start_pipeline_trade_raise_generic_error,
    spy_start_pipeline_trade
):
    app = create_app(testing=True)
    return app


@pytest.fixture
def client_with_open_positions(app_with_open_positions):
    with app_with_open_positions.test_client() as client:
        yield client
