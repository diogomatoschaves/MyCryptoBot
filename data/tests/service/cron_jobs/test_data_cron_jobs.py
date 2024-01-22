import pytest

from data.service.cron_jobs.check_app_is_running import check_app_is_running
from data.tests.setup.fixtures.internal_modules import mock_stop_instance, spy_stop_instance
from shared.utils.tests.fixtures.models import *

API_PREFIX = '/api'


class TestCronJobs:

    def test_check_app_is_running(
        self,
        create_all_pipelines,
        mock_stop_instance,
        spy_stop_instance
    ):
        check_app_is_running()

        assert spy_stop_instance.call_count == 2
