from data.service.external_requests import generate_signal
from data.service.helpers import MODEL_APP_ENDPOINTS
from data.sources._signal_triggerer import wait_for_job_conclusion
from data.sources import trigger_signal
from shared.utils.tests.fixtures.external_modules import mock_time_sleep
from data.tests.setup.fixtures.internal_modules import *
from data.tests.setup.fixtures.external_modules import *
from shared.utils.exceptions import FailedSignalGeneration

from pytest_mock import mocker
import pytest


class TestExternalRequests:

    @pytest.mark.parametrize(
        "side_effects,expected_value",
        [
            pytest.param(
                [
                    {"code": "FINISHED", "status": "finished"},
                ],
                True,
                id="STATUS_FINISHED",
            ),
            pytest.param(
                [
                    {"code": "IN_QUEUE", "status": "in-queue"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "FINISHED", "status": "finished"},
                ],
                True,
                id="STATUS_WAITING_IN-QUEUE",
            ),
            pytest.param(
                [
                    {"code": "FAILED", "status": "failed"},
                ],
                False,
                id="STATUS_FAILED",
            ),
            pytest.param(
                [
                    {"code": "JOB_NOT_FOUND", "status": "job not found"},
                    {"code": "FINISHED", "status": "finished"},
                ],
                True,
                id="STATUS_NOT_FOUND",
            ),
        ],
    )
    def test_wait_for_job_conclusion(
        self,
        side_effects,
        expected_value,
        mock_check_job_status_response,
        mock_generate_signal,
        mock_time_sleep,
    ):
        """
        GIVEN some params
        WHEN the method generate_signal is called
        THEN the return value is equal to the expected response

        """

        mock_generate_signal.side_effect = [{"success": True, "job_id": 'abcdef'}] * len(side_effects)
        mock_check_job_status_response.side_effect = side_effects

        params = {
            "job_id": "abcdef",
            "pipeline_id": 1,
            "retry": 0
        }

        res = wait_for_job_conclusion(**params)

        assert res == expected_value

        assert mock_check_job_status_response.call_count == len(side_effects)

    def test_wait_for_job_conclusion_job_not_found(
        self,
        mock_check_job_status_response,
        mock_generate_signal,
        mock_time_sleep
    ):

        mock_generate_signal.return_value = {"success": True, "job_id": 'abcdef'}

        mock_check_job_status_response.side_effect = [
            {"code": "JOB_NOT_FOUND", "status": "job not found"},
            {"code": "JOB_NOT_FOUND", "status": "job not found"},
            {"code": "JOB_NOT_FOUND", "status": "job not found"},
            {"code": "JOB_NOT_FOUND", "status": "job not found"},
            {"code": "JOB_NOT_FOUND", "status": "job not found"},
            {"code": "FINISHED", "status": "finished"},
        ]

        params = {
            "job_id": "abcdef",
            "pipeline_id": 1,
            "retry": 0
        }

        res = wait_for_job_conclusion(**params)

        assert res is False

    @pytest.mark.parametrize(
        "return_value,expected_value",
        [
            pytest.param(
                {"success": True, "job_id": 'abcdef'},
                True,
                id="SUCCESS",
            ),
            pytest.param(
                {"success": False, "message": "Failed"},
                False,
                id="FAIL",
            )
        ],
    )
    def test_trigger_signal(
        self,
        return_value,
        expected_value,
        mock_generate_signal,
        mock_wait_for_job_conclusion,
    ):
        """
        GIVEN some params
        WHEN the method generate_signal is called
        THEN the return value is equal to the expected response

        """

        mock_generate_signal.return_value = return_value
        mock_wait_for_job_conclusion.return_value = True

        params = {
            "pipeline_id": 1,
            "retry": 0
        }

        res = trigger_signal(**params)

        assert res is expected_value
