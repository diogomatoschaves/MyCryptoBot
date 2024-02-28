import pytest

from data.service.cron_jobs.app_health import check_app_health
from data.tests.setup.fixtures.internal_modules import (
    mock_stop_instance,
    spy_stop_instance,
    mock_get_open_positions,
    mock_redis_connection_external_requests,
    mock_get_open_positions_unsuccessful
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
        spy_stop_instance,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert spy_stop_instance.call_count == 2
        assert requests_post_spy.call_count == 3

    @pytest.mark.slow
    def test_check_app_health_failed_stop(
        self,
        create_pipeline,
        create_paper_trading_pipeline,
        mock_stop_instance,
        spy_stop_instance,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests,
        patch_time_sleep
    ):
        mock_stop_instance.side_effect = [True, False, False, True]

        check_app_health()

        assert spy_stop_instance.call_count == 1
        assert requests_post_spy.call_count == 2

    @pytest.mark.slow
    def test_check_app_health_remote_positions(
        self,
        create_pipeline_BNBBTC,
        create_open_position_pipeline_10,
        mock_stop_instance,
        spy_stop_instance,
        mock_get_open_positions,
        mock_requests_post,
        requests_post_spy,
        mock_redis_connection_external_requests,
        patch_time_sleep,
        patch_datetime_future
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert spy_stop_instance.call_count == 1
        spy_stop_instance.assert_called_with(10, '', force=True, raise_exception=False)

        pipeline = Pipeline.objects.get(id=10)
        position = Position.objects.get(pipeline__id=10)

        assert pipeline.active is False
        assert pipeline.units == 0
        assert pipeline.balance == pipeline.current_equity * pipeline.leverage
        assert position.position == 0

    @pytest.mark.slow
    def test_check_app_health_get_positions_error(
        self,
        spy_stop_instance,
        requests_post_spy,
        mock_get_open_positions_unsuccessful,
        patch_time_sleep
    ):
        mock_stop_instance.return_value = True

        check_app_health()

        assert spy_stop_instance.call_count == 0
        assert requests_post_spy.call_count == 0
