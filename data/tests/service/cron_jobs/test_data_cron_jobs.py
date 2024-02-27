import pytest

from data.service.cron_jobs.check_app_is_running import check_app_is_running
from data.tests.setup.fixtures.internal_modules import mock_stop_instance, spy_stop_instance
from data.tests.setup.fixtures.external_modules import patch_time_sleep
from shared.utils.tests.fixtures.models import *

API_PREFIX = '/api'


class TestCronJobs:

    @pytest.mark.slow
    def test_check_app_is_running(
        self,
        create_all_pipelines,
        mock_stop_instance,
        spy_stop_instance
    ):
        mock_stop_instance.return_value = True

        check_app_is_running()

        assert spy_stop_instance.call_count == 2

    @pytest.mark.slow
    def test_check_app_is_running_failed_stop(
        self,
        create_all_pipelines,
        mock_stop_instance,
        spy_stop_instance,
        patch_time_sleep
    ):
        mock_stop_instance.side_effect = [True, False, False, True]

        check_app_is_running()

        assert spy_stop_instance.call_count == 2
