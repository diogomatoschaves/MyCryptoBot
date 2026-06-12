import pytest

from data.service.cron_jobs.app_health import check_app_health
from data.tests.setup.fixtures.internal_modules import (
    mock_stop_instance,
    spy_stop_pipeline,
    spy_stop_instance,
    mock_get_open_positions,
    mock_redis_connection_external_requests,
    mock_get_open_positions_unsuccessful,
    mock_redis_connection_bots_api_helpers,
    mock_start_stop_symbol_trading_success_true,
    spy_start_stop_symbol_trading,
    mock_config_no_restart,
    mock_config_no_retries
)
from data.tests.setup.fixtures.external_modules import patch_time_sleep, patch_datetime_future
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.fixtures.external_modules import mock_requests_post, requests_post_spy

API_PREFIX = '/api'


class TestCronJobs:
    @pytest.mark.slow
    def test_check_app_health(
        self,
        create_pipeline,
        create_pipeline_with_balance,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_start_stop_symbol_trading_success_true,
        mock_redis_connection_bots_api_helpers,
        mock_redis_connection_external_requests,
        spy_start_stop_symbol_trading
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert spy_stop_pipeline.call_count == 2
        assert requests_post_spy.call_count == 3
        assert spy_start_stop_symbol_trading.call_count == 2

        pipeline_1 = Pipeline.objects.get(id=1)
        pipeline_4 = Pipeline.objects.get(id=1)

        assert pipeline_1.restarted == 1
        assert pipeline_4.restarted == 1

    @pytest.mark.slow
    def test_check_app_health_failed_stop(
        self,
        create_pipeline,
        create_paper_trading_pipeline,
        mock_stop_instance,
        spy_stop_pipeline,
        spy_stop_instance,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_start_stop_symbol_trading_success_true,
        spy_start_stop_symbol_trading,
        patch_time_sleep
    ):
        mock_stop_instance.side_effect = [False, False, False, False, False, True]

        check_app_health()

        assert spy_stop_instance.call_count == 5
        assert spy_stop_pipeline.call_count == 1
        assert requests_post_spy.call_count == 2

    @pytest.mark.slow
    def test_check_app_health_no_restart(
        self,
        create_pipeline,
        create_paper_trading_pipeline,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_start_stop_symbol_trading_success_true,
        spy_start_stop_symbol_trading,
        mock_config_no_restart,
        patch_time_sleep
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert spy_stop_pipeline.call_count == 1
        assert requests_post_spy.call_count == 0

        assert spy_start_stop_symbol_trading.call_count == 0

    @pytest.mark.slow
    def test_check_app_health_no_retries(
        self,
        create_pipeline,
        create_paper_trading_pipeline,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_start_stop_symbol_trading_success_true,
        spy_start_stop_symbol_trading,
        mock_config_no_retries,
        patch_time_sleep
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert spy_stop_pipeline.call_count == 1
        assert requests_post_spy.call_count == 0

        assert spy_start_stop_symbol_trading.call_count == 0

    @pytest.mark.slow
    def test_check_app_health_remote_positions(
        self,
        create_pipeline_BNBBTC,
        create_open_position_pipeline_10,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_start_stop_symbol_trading_success_true,
        mock_config_no_restart,
        patch_time_sleep,
        patch_datetime_future
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert spy_stop_pipeline.call_count == 1
        spy_stop_pipeline.assert_called_with(10, '', force=True, raise_exception=False)

        pipeline = Pipeline.objects.get(id=10)
        position = Position.objects.get(pipeline__id=10)

        assert pipeline.active is False
        assert pipeline.units == 0
        assert pipeline.balance == pipeline.current_equity * pipeline.leverage
        assert position.position == 0

    @pytest.mark.slow
    def test_check_app_health_get_positions_error(
        self,
        spy_stop_pipeline,
        requests_post_spy,
        mock_get_open_positions_unsuccessful,
        patch_time_sleep
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert spy_stop_pipeline.call_count == 0
        assert requests_post_spy.call_count == 0


import datetime

import pytz

import data.service.cron_jobs.app_health._app_health as app_health_module
from data.service.cron_jobs.app_health._app_health import (
    POSITION_MISMATCH_GRACE, RESTART_COUNTER_RESET_AFTER,
)


@pytest.fixture
def mock_send_alert(mocker):
    return mocker.patch.object(app_health_module, 'send_alert')


class TestCronJobAlerts:

    @pytest.mark.slow
    def test_stuck_and_mismatch_fire_alerts(
        self,
        create_pipeline_BNBBTC,
        create_open_position_pipeline_10,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_start_stop_symbol_trading_success_true,
        mock_config_no_restart,
        patch_time_sleep,
        patch_datetime_future,
        mock_send_alert,
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert mock_send_alert.call_count >= 1
        severities = [call.kwargs["severity"] for call in mock_send_alert.call_args_list]
        assert "critical" in severities

    @pytest.mark.slow
    def test_restart_exhausted_fires_critical_alert(
        self,
        create_pipeline_BNBBTC,
        create_open_position_pipeline_10,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_start_stop_symbol_trading_success_true,
        mock_config_no_retries,
        patch_time_sleep,
        patch_datetime_future,
        mock_send_alert,
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        titles = [call.kwargs["title"] for call in mock_send_alert.call_args_list]
        assert "Pipeline restart retries exhausted" in titles

    @pytest.mark.slow
    def test_restarted_counter_resets_after_sustained_health(
        self,
        create_pipeline,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_config_no_restart,
        patch_time_sleep,
        mock_send_alert,
    ):
        now = datetime.datetime.now(pytz.utc)
        Pipeline.objects.filter(id=1).update(
            restarted=1,
            last_entry=now - datetime.timedelta(minutes=1),
            open_time=now - RESTART_COUNTER_RESET_AFTER - datetime.timedelta(minutes=5),
        )

        check_app_health()

        assert spy_stop_pipeline.call_count == 0
        assert Pipeline.objects.get(id=1).restarted == 0

    @pytest.mark.slow
    def test_mismatch_within_grace_period_is_not_stopped(
        self,
        create_pipeline_BNBBTC,
        create_open_position_pipeline_10,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_config_no_restart,
        patch_time_sleep,
        mock_send_alert,
    ):
        now = datetime.datetime.now(pytz.utc)
        Pipeline.objects.filter(id=10).update(
            last_entry=now - datetime.timedelta(minutes=1),
            open_time=now - POSITION_MISMATCH_GRACE + datetime.timedelta(minutes=5),
        )

        check_app_health()

        assert spy_stop_pipeline.call_count == 0
        assert Pipeline.objects.get(id=10).active is True
