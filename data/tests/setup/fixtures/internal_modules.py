import os
from collections import namedtuple
from datetime import datetime, timedelta

import pytest
import pytz
from django.db import InterfaceError

import data
from data.service.helpers.exceptions import PipelineStartFail, DataPipelineCouldNotBeStopped
from data.sources.binance import BinanceDataHandler
from data.tests.setup.test_data.sample_data import mock_websocket_raw_data_5m, mock_websocket_raw_data_1h, STRATEGIES
from database.model.models import Pipeline

MODEL_APP_URL = 'https://example.com'
EXECUTION_APP_URL = 'https://example.com'


@pytest.fixture()
def mock_settings_env_vars(mocker):
    mocker.patch.dict(os.environ, {
        "MODEL_APP_URL": MODEL_APP_URL,
        "EXECUTION_APP_URL": EXECUTION_APP_URL,
    })


@pytest.fixture
def mock_trigger_signal_successfully(mocker):
    return mocker.patch.object(
        data.sources.binance._binance,
        'trigger_signal',
        lambda pipeline_id, header='': (True, ""),
    )


@pytest.fixture
def mock_trigger_signal_fail(mocker):
    mocker.patch.object(
        data.sources.binance._binance,
        'trigger_signal',
        lambda pipeline_id, header='': (False, ""),
    )


@pytest.fixture
def trigger_signal_spy(mocker):
    return mocker.spy(data.sources.binance._binance, 'trigger_signal')


def double_callback(callback, mock_row):
    callback(mock_row[0])
    callback(mock_row[1])


def mock_start_multiplex_socket(self, callback, streams):
    double_callback(callback, mock_websocket_raw_data_5m)
    double_callback(callback, mock_websocket_raw_data_1h)

    return f"streams={'/'.join(streams)}"


@pytest.fixture
def mock_binance_handler_websocket(mocker):
    mocker.patch.object(BinanceDataHandler, "start_multiplex_socket", mock_start_multiplex_socket)


@pytest.fixture
def mock_binance_websocket_start(mocker):
    mocker.patch.object(BinanceDataHandler, "start", lambda self: None)


@pytest.fixture
def mock_binance_websocket_stop(mocker):
    mocker.patch.object(BinanceDataHandler, "_stop_websocket", lambda self: None)


@pytest.fixture
def mock_binance_handler_start_data_ingestion(mocker):
    mocker.patch.object(
        BinanceDataHandler,
        "start_data_ingestion",
        lambda self, header='': None
    )


def fake_stop_data_ingestion(self, header, raise_exception, force):
    Pipeline.objects.filter(id=1).update(active=False)
    return True


@pytest.fixture
def mock_binance_handler_stop_data_ingestion(mocker):
    return mocker.patch.object(
        BinanceDataHandler,
        "stop_data_ingestion",
        fake_stop_data_ingestion
    )


@pytest.fixture
def binance_handler_stop_data_ingestion_spy(mocker):
    return mocker.spy(BinanceDataHandler, 'stop_data_ingestion')


@pytest.fixture
def binance_handler_instances_spy_start_bot(mocker):
    return mocker.patch('data.service.blueprints.bots_api._helpers.binance_instances', new_callable=list)


def immediate_execution(initialize_data_collection, pipeline_id, header=''):
    return initialize_data_collection(pipeline_id, header)


@pytest.fixture
def mock_executor_submit(mocker):
    mocker.patch.object(
        data.service.blueprints.bots_api._helpers.executor,
        "submit",
        immediate_execution
    )


@pytest.fixture
def fake_executor_submit(mocker):
    mocker.patch.object(
        data.service.blueprints.bots_api._helpers.executor,
        "submit",
        lambda x, y, z=None: None
    )


@pytest.fixture
def binance_handler_instances_spy_stop_bot(db, create_symbol, create_assets, create_exchange, mocker):
    return mocker.patch(
        'data.service.blueprints.bots_api._helpers.binance_instances',
        [
            BinanceDataHandler(symbol='BTCUSDT', candle_size="1h", pipeline_id=1),
            BinanceDataHandler(symbol='BTCUSDT', candle_size="1h", pipeline_id=2)
        ]
    )


def fake_start_stop_trading(pipeline_id, start_or_stop):
    if start_or_stop == 'stop':
        Pipeline.objects.get(id=pipeline_id).update(active=False)

    return {"success": True, "message": '', "code": ""}


@pytest.fixture
def mock_start_stop_symbol_trading_success_true(mocker):
    mocker.patch.object(
        data.service.blueprints.bots_api._helpers,
        'start_stop_symbol_trading',
        fake_start_stop_trading,
    )


@pytest.fixture
def spy_start_stop_symbol_trading(mocker):
    return mocker.spy(data.service.blueprints.bots_api._helpers, 'start_stop_symbol_trading')


@pytest.fixture
def mock_start_stop_symbol_trading_success_true_binance_handler(mocker):
    mocker.patch.object(
        data.sources.binance._binance,
        'start_stop_symbol_trading',
        lambda pipeline_id, start_or_stop: {"success": True, "message": '', "code": ""},
    )


@pytest.fixture
def mock_start_stop_symbol_trading(mocker):
    return mocker.patch('data.sources.binance._binance.start_stop_symbol_trading')


@pytest.fixture
def mock_start_stop_symbol_trading_success_false(mocker):
    return mocker.patch.object(
        data.service.blueprints.bots_api._helpers,
        'start_stop_symbol_trading',
        lambda payload, start_or_stop: {"success": False, "message": "Pipeline could not be started.", "code": ""},
    )


def raise_pipeline_stop_fail(pipeline_id, header, raise_exception):
    if raise_exception:
        raise DataPipelineCouldNotBeStopped("APIError(code=-1021): "
                                            "Timestamp for this request is outside of the recvWindow.")


@pytest.fixture
def mock_stop_instance_raise_exception(mocker):
    return mocker.patch.object(
        data.service.blueprints.bots_api._bots_api,
        'stop_instance',
        raise_pipeline_stop_fail,
    )


@pytest.fixture
def mock_stop_instance(mocker):
    return mocker.patch(
        'data.service.blueprints.bots_api._helpers.stop_instance',
    )


@pytest.fixture
def spy_stop_instance(mocker):
    return mocker.spy(data.service.blueprints.bots_api._helpers, 'stop_instance')


@pytest.fixture
def spy_stop_pipeline(mocker):
    return mocker.spy(data.service.cron_jobs.app_health._app_health, 'stop_pipeline')


@pytest.fixture
def mock_check_job_status_response(mocker):
    return mocker.patch(
        'data.sources._signal_triggerer.check_job_status',
    )


@pytest.fixture
def mock_generate_signal(mocker):
    return mocker.patch(
        'data.sources._signal_triggerer.generate_signal',
    )


@pytest.fixture
def mock_wait_for_job_conclusion(mocker):
    return mocker.patch(
        'data.sources._signal_triggerer.wait_for_job_conclusion',
    )


def mock_redis():
    class RedisCache:

        def __init__(self):
            setattr(self, "bearer_token", "mock bearer_token")

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
    return mocker.patch("data.service.app.cache", mock_redis())


@pytest.fixture
def mock_redis_connection_external_requests(mocker):
    return mocker.patch("data.service.external_requests.cache", mock_redis())


@pytest.fixture
def mock_redis_connection_bots_api(mocker):
    return mocker.patch("data.service.blueprints.bots_api._bots_api.cache", mock_redis())


@pytest.fixture
def mock_redis_connection_bots_api_helpers(mocker):
    return mocker.patch("data.service.blueprints.bots_api._helpers.cache", mock_redis())


@pytest.fixture
def mock_redis_connection_binance(mocker):
    return mocker.patch("data.sources.binance._binance.cache", mock_redis())


@pytest.fixture
def mock_redis_connection_user_mgmt(mocker):
    return mocker.patch("data.service.blueprints.user_management.cache", mock_redis())


@pytest.fixture
def mock_get_jwt(mocker):
    return mocker.patch.object(
        data.service.blueprints.user_management,
        'get_jwt',
        lambda: {"exp": datetime.timestamp(datetime.now(pytz.utc) + timedelta(minutes=10))}
    )


@pytest.fixture
def mock_get_strategies_raise_exception(mocker):
    return mocker.patch('data.service.blueprints.dashboard.get_strategies')


@pytest.fixture
def spy_start_symbol_trading(mocker):
    return mocker.spy(data.service.app, 'start_symbol_trading')

def fake_get_strategies_error():
    raise InterfaceError


def fake_get_strategies_no_error():
    return STRATEGIES


class SideEffect:
    def __init__(self, *fns):
        self.fs = iter(fns)

    def __call__(self, *args, **kwargs):
        f = next(self.fs)
        return f(*args, **kwargs)


@pytest.fixture
def mock_get_strategies(mocker):
    mocker.patch.object(data.service.blueprints.bots_api._bots_api, "get_strategies", fake_get_strategies_no_error)


@pytest.fixture
def mock_get_strategies_dashboard(mocker):
    mocker.patch.object(data.service.blueprints.dashboard, "get_strategies", fake_get_strategies_no_error)


get_strategies_side_effect_3_errors = SideEffect(
    fake_get_strategies_error, fake_get_strategies_error, fake_get_strategies_error
)

get_strategies_side_effect_2_errors = SideEffect(
    fake_get_strategies_error, fake_get_strategies_error, fake_get_strategies_no_error
)

get_strategies_side_effect_1_errors = SideEffect(
    fake_get_strategies_error, fake_get_strategies_no_error, fake_get_strategies_no_error
)

get_strategies_side_effect_0_errors = SideEffect(
    fake_get_strategies_no_error, fake_get_strategies_no_error, fake_get_strategies_no_error
)


def mock_positions():
    return {
        "success": True,
        "positions": {
            "testnet": [{"symbol": "BTCUSDT", "units": 0.01}, {"symbol": "ETHUSDT", "units": -0.01}],
            "live": [{"symbol": "BTCUSDT", "units": 0.01}, {"symbol": "ETHUSDT", "units": -0.01}],
        }
    }


@pytest.fixture
def mock_get_open_positions(mocker):
    mocker.patch.object(data.service.cron_jobs.app_health._app_health, 'get_open_positions', mock_positions)


@pytest.fixture
def mock_get_open_positions_unsuccessful(mocker):
    mocker.patch.object(data.service.cron_jobs.app_health._app_health, 'get_open_positions', lambda: {"success": False})


FakeConfig = namedtuple(
    'fake_config',
    [
        'check_inconsistencies',
        'restart_failed_pipelines',
        'restart_retries',
        'redis_url'
    ]
)
fake_config_no_restart = FakeConfig('false', 'false', '2', '')
fake_config_no_retries = FakeConfig('false', 'true', '0', '')


@pytest.fixture
def mock_config_no_restart(mocker):
    mocker.patch('data.service.cron_jobs.app_health._app_health.config', fake_config_no_restart)


@pytest.fixture
def mock_config_no_retries(mocker):
    mocker.patch('data.service.cron_jobs.app_health._app_health.config', fake_config_no_retries)
