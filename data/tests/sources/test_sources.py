from data.service.external_requests import generate_signal
from data.service.helpers import MODEL_APP_ENDPOINTS
from data.sources._signal_triggerer import wait_for_job_conclusion, RESPONSES
from data.sources import trigger_signal
from shared.utils.tests.fixtures.external_modules import mock_time_sleep
from shared.utils.tests.fixtures.models import *
from data.tests.setup.fixtures.internal_modules import *
from data.tests.setup.fixtures.external_modules import *

from pytest_mock import mocker
import pytest


class TestExternalRequests:

    @pytest.mark.parametrize(
        "side_effects,expected_value",
        [
            pytest.param(
                [
                    {"code": "FINISHED", "success": True, "status": "finished"},
                ],
                RESPONSES["SUCCESS"],
                id="STATUS_FINISHED-SUCCESS",
            ),
            pytest.param(
                [
                    {"code": "FINISHED", "success": False, "status": "finished"},
                ],
                RESPONSES["JOB_FAILED"],
                id="STATUS_FINISHED-FAIL",
            ),
            pytest.param(
                [
                    {"code": "IN_QUEUE", "status": "in-queue"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "FINISHED", "success": True, "status": "finished"},
                ],
                RESPONSES["SUCCESS"],
                id="STATUS_WAITING_IN-QUEUE",
            ),
            pytest.param(
                [
                    {"code": "FAILED", "status": "failed"},
                ],
                RESPONSES["JOB_FAILED"],
                id="STATUS_FAILED",
            ),
            pytest.param(
                [
                    {"code": "JOB_NOT_FOUND", "status": "job not found"},
                    {"code": "FINISHED", "success": True, "status": "finished"},
                ],
                RESPONSES["SUCCESS"],
                id="STATUS_NOT_FOUND_ONCE",
            ),
            pytest.param(
                [
                    {"code": "JOB_NOT_FOUND", "status": "job not found"},
                    {"code": "JOB_NOT_FOUND", "status": "job not found"},
                    {"code": "JOB_NOT_FOUND", "status": "job not found"},
                ],
                RESPONSES["JOB_NOT_FOUND"],
                id="STATUS_JOB_NOT_FOUND_THREE_TIMES",
            ),
            pytest.param(
                [
                    {"code": "IN_QUEUE", "status": "in-queue"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                    {"code": "WAITING", "status": "waiting"},
                ],
                RESPONSES["TOO_MANY_RETRIES"],
                id="STATUS_TOO_MANY_RETRIES",
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
        mock_redis_connection_external_requests,
        create_pipeline
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

    @pytest.mark.parametrize(
        "generate_signal_return_value,wait_for_job_conclusion_return_value,expected_value",
        [
            pytest.param(
                {"success": True, "job_id": 'abcdef'},
                (True, ""),
                RESPONSES["SUCCESS"],
                id="True-True-SUCCESS",
            ),
            pytest.param(
                {"success": True, "job_id": 'abcdef'},
                (False, 'Stopping Pipeline. Job failed.'),
                RESPONSES["JOB_FAILED"],
                id="True-False-FAIL",
            ),
            pytest.param(
                {"success": False, "message": "Failed"},
                (True, ""),
                (False, "Failed"),
                id="FAIL",
            )
        ],
    )
    def test_trigger_signal(
        self,
        generate_signal_return_value,
        wait_for_job_conclusion_return_value,
        expected_value,
        mock_generate_signal,
        mock_wait_for_job_conclusion,
        mock_redis_connection_external_requests,
        create_pipeline
    ):
        """
        GIVEN some params
        WHEN the method generate_signal is called
        THEN the return value is equal to the expected response

        """

        mock_generate_signal.return_value = generate_signal_return_value
        mock_wait_for_job_conclusion.return_value = wait_for_job_conclusion_return_value

        params = {
            "pipeline_id": 1,
            "retry": 0
        }

        res = trigger_signal(**params)

        assert res == expected_value

    @pytest.mark.parametrize(
        "pipeline_id,expected_value",
        [
            pytest.param(
                3,
                RESPONSES["PIPELINE_NOT_ACTIVE"],
                id="INACTIVE_PIPELINE",
            ),
            pytest.param(
                2,
                RESPONSES["PIPELINE_NOT_ACTIVE"],
                id="NON_EXISTENT_PIPELINE",
            )
        ],
    )
    def test_trigger_signal_inactive_pipeline(
        self,
        pipeline_id,
        expected_value,
        mock_generate_signal,
        mock_wait_for_job_conclusion,
        mock_redis_connection_external_requests,
        create_inactive_pipeline
    ):
        """
        GIVEN some params
        WHEN the method generate_signal is called
        THEN the return value is equal to the expected response

        """
        params = {
            "pipeline_id": pipeline_id,
            "retry": 0
        }

        res = trigger_signal(**params)

        assert res == expected_value
