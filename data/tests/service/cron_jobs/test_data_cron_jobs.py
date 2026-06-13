import pytest

from data.service.cron_jobs.app_health import check_app_health
from data.tests.setup.fixtures.internal_modules import (
    fake_executor_submit,
    mock_redis_connection_app_health,
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
from data.tests.setup.fixtures.external_modules import patch_time_sleep, patch_datetime_future, FUTURE_TIME
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.fixtures.external_modules import mock_requests_post, requests_post_spy

API_PREFIX = '/api'


class TestCronJobs:
    @pytest.mark.slow
    def test_check_app_health(
        self,
        fake_executor_submit,
        mock_redis_connection_app_health,
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
        fake_executor_submit,
        mock_redis_connection_app_health,
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
        fake_executor_submit,
        mock_redis_connection_app_health,
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
        fake_executor_submit,
        mock_redis_connection_app_health,
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
        fake_executor_submit,
        mock_redis_connection_app_health,
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

        # keep last_entry fresh so only the mismatch branch fires.
        # NOTE: patch_datetime_future replaces the global datetime.datetime
        # class, which breaks Django's isinstance checks for real datetime
        # instances (they get truncated to date-only on save) - so the value
        # must be built from the (patched) class itself
        fresh = FUTURE_TIME - datetime.timedelta(minutes=1)
        fresh = datetime.datetime(
            fresh.year, fresh.month, fresh.day, fresh.hour, fresh.minute,
            tzinfo=pytz.utc,
        )
        Pipeline.objects.filter(id=10).update(last_entry=fresh)


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

import data.service.cron_jobs.app_health._app_health as app_health_module  # noqa: E402
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
        fake_executor_submit,
        mock_redis_connection_app_health,
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

        # keep last_entry fresh so only the mismatch branch fires.
        # NOTE: patch_datetime_future replaces the global datetime.datetime
        # class, which breaks Django's isinstance checks for real datetime
        # instances (they get truncated to date-only on save) - so the value
        # must be built from the (patched) class itself
        fresh = FUTURE_TIME - datetime.timedelta(minutes=1)
        fresh = datetime.datetime(
            fresh.year, fresh.month, fresh.day, fresh.hour, fresh.minute,
            tzinfo=pytz.utc,
        )
        Pipeline.objects.filter(id=10).update(last_entry=fresh)

        check_app_health()

        assert mock_send_alert.call_count >= 1
        severities = [call.kwargs["severity"] for call in mock_send_alert.call_args_list]
        assert "critical" in severities

    @pytest.mark.slow
    def test_restart_exhausted_fires_critical_alert(
        self,
        fake_executor_submit,
        mock_redis_connection_app_health,
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
        fake_executor_submit,
        mock_redis_connection_app_health,
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
        fake_executor_submit,
        mock_redis_connection_app_health,
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


class TestNeverIngestedWatchdog:
    """The user-reported zombie: a bot that starts, never ingests a single
    candle (last_entry stays None), and used to escape the stuck check."""

    @pytest.fixture
    def mock_publish_event(self, mocker):
        return mocker.patch.object(app_health_module, 'publish_pipeline_event')

    @pytest.fixture
    def base_mocks(
        self,
        fake_executor_submit,
        mock_redis_connection_app_health,
        create_pipeline_BNBBTC,
        mock_stop_instance,
        spy_stop_pipeline,
        mock_get_open_positions,
        mock_redis_connection_external_requests,
        mock_redis_connection_bots_api_helpers,
        mock_config_no_restart,
        patch_time_sleep,
        mock_send_alert,
        mock_publish_event,
    ):
        mock_stop_instance.return_value = True
        return {
            "stop": spy_stop_pipeline,
            "alert": mock_send_alert,
            "event": mock_publish_event,
            "redis": mock_redis_connection_app_health,
        }

    def test_never_ingested_pipeline_is_flagged(self, base_mocks):
        now = datetime.datetime.now(pytz.utc)
        Pipeline.objects.filter(id=10).update(
            last_entry=None, open_time=now - datetime.timedelta(minutes=20)
        )

        check_app_health()

        assert base_mocks["stop"].call_count == 1
        assert "never ingested" in base_mocks["alert"].call_args.kwargs["body"]
        assert base_mocks["event"].call_count == 1

    def test_loading_pipeline_within_budget_is_untouched(self, base_mocks):
        import json as json_module
        base_mocks["redis"].set("Loading", json_module.dumps([10]))

        now = datetime.datetime.now(pytz.utc)
        Pipeline.objects.filter(id=10).update(
            last_entry=None, open_time=now - datetime.timedelta(minutes=20)
        )

        check_app_health()

        assert base_mocks["stop"].call_count == 0
        assert Pipeline.objects.get(id=10).active is True

    def test_loading_pipeline_beyond_budget_is_flagged(self, base_mocks):
        import json as json_module
        base_mocks["redis"].set("Loading", json_module.dumps([10]))

        now = datetime.datetime.now(pytz.utc)
        Pipeline.objects.filter(id=10).update(
            last_entry=None, open_time=now - datetime.timedelta(hours=2)
        )

        check_app_health()

        assert base_mocks["stop"].call_count == 1
        assert "load still incomplete" in base_mocks["alert"].call_args.kwargs["body"]


class TestReviewRegressions:
    """Fixes from the PR review: mismatch cleanup must run even when the
    stuck check already stopped the pipeline; broken rows must not abort
    the whole health-check run."""

    @pytest.fixture
    def mock_publish_event(self, mocker):
        return mocker.patch.object(app_health_module, 'publish_pipeline_event')

    @pytest.fixture
    def base_mocks(
        self,
        fake_executor_submit,
        mock_redis_connection_app_health,
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
        mock_publish_event,
    ):
        mock_stop_instance.return_value = True
        return {"stop": spy_stop_pipeline, "alert": mock_send_alert}

    def test_stuck_and_mismatched_pipeline_still_gets_mismatch_cleanup(self, base_mocks):
        # stuck (never ingested) AND position-mismatched: the stuck check
        # stops the pipeline, but the mismatch cleanup must still restore
        # the balance and reset the Position row
        now = datetime.datetime.now(pytz.utc)
        Pipeline.objects.filter(id=10).update(
            last_entry=None,
            open_time=now - datetime.timedelta(minutes=20),
            current_equity=500,
            leverage=2,
            balance=123,
            units=0.5,
        )

        check_app_health()

        # stopped exactly once (by the stuck check - no duplicate stop)
        assert base_mocks["stop"].call_count == 1

        pipeline = Pipeline.objects.get(id=10)
        assert pipeline.units == 0
        assert pipeline.balance == 500 * 2
        assert Position.objects.get(pipeline__id=10).position == 0

    def test_active_pipeline_without_open_time_does_not_crash_run(self, base_mocks):
        Pipeline.objects.filter(id=10).update(last_entry=None, open_time=None)

        # must not raise: the mismatch check treats a missing open_time as
        # grace-elapsed and still performs its cleanup
        check_app_health()

        assert Position.objects.get(pipeline__id=10).position == 0

    def test_one_broken_pipeline_does_not_abort_other_checks(self, base_mocks, mocker):
        Pipeline.objects.create(
            id=11, name="Second", symbol_id="BTCUSDT", exchange_id="binance",
            interval="1h", active=True, initial_equity=1000, leverage=1,
            balance=0, units=0,
            last_entry=datetime.datetime.now(pytz.utc) - datetime.timedelta(hours=2),
            open_time=datetime.datetime.now(pytz.utc) - datetime.timedelta(hours=3),
        )

        stuck_check = mocker.patch.object(
            app_health_module, 'check_pipeline_stuck',
            side_effect=[RuntimeError("broken row"), True],
        )

        check_app_health()

        # both pipelines were attempted despite the first raising
        assert stuck_check.call_count == 2
        # the failure was alerted, not swallowed silently
        titles = [call.kwargs["title"] for call in base_mocks["alert"].call_args_list]
        assert "Health check failed for a pipeline" in titles
