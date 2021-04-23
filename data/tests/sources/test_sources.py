from data.service.external_requests import generate_signal
from data.service.helpers import MODEL_APP_ENDPOINTS
from data.sources._sources import wait_for_job_conclusion, trigger_signal
from data.tests.setup.fixtures.external_modules import mock_time_sleep
from data.tests.setup.fixtures.internal_modules import *
from shared.utils.exceptions import FailedSignalGeneration


class TestExternalRequests:

    @pytest.mark.parametrize(
        "side_effects,expected_value",
        [
            pytest.param(
                [
                    {"status": "finished"},
                ],
                True,
                id="STATUS_FINISHED",
            ),
            pytest.param(
                [
                    {"status": "in-queue"},
                    {"status": "waiting"},
                    {"status": "waiting"},
                    {"status": "finished"},
                ],
                True,
                id="STATUS_WAITING_IN-QUEUE",
            ),
            pytest.param(
                [
                    {"status": "failed"},
                ],
                False,
                id="STATUS_FAILED",
            ),
            pytest.param(
                [
                    {"status": "job not found"},
                    {"status": "finished"},
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
        mock_time_sleep
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
            "symbol": "BTCUSDT",
            "strategy": "MovingAverage",
            "params": {"sma": 30},
            "candle_size": "1h",
            "exchange": "Binance",
            "retry": 0
        }

        res = wait_for_job_conclusion(**params)

        assert res == expected_value

        assert mock_check_job_status_response.call_count == len(side_effects)

    def test_wait_for_job_conclusion_exception(
        self,
        mock_check_job_status_response,
        mock_generate_signal,
        mock_time_sleep
    ):

        mock_generate_signal.return_value = {"success": True, "job_id": 'abcdef'}

        mock_check_job_status_response.side_effect = [
            {"status": "job not found"},
            {"status": "job not found"},
            {"status": "job not found"},
            {"status": "job not found"},
            {"status": "job not found"},
            {"status": "finished"},
        ]

        params = {
            "job_id": "abcdef",
            "symbol": "BTCUSDT",
            "strategy": "MovingAverage",
            "params": {"sma": 30},
            "candle_size": "1h",
            "exchange": "Binance",
            "retry": 0
        }

        with pytest.raises(Exception) as excinfo:
            res = wait_for_job_conclusion(**params)

        assert excinfo.type == FailedSignalGeneration

    @pytest.mark.parametrize(
        "return_value,expected_value",
        [
            pytest.param(
                {"success": True, "job_id": 'abcdef'},
                True,
                id="SUCCESS",
            ),
            pytest.param(
                {"success": False, "response": "Failed"},
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
        mock_wait_for_job_conclusion
    ):
        """
        GIVEN some params
        WHEN the method generate_signal is called
        THEN the return value is equal to the expected response

        """

        mock_generate_signal.return_value = return_value
        mock_wait_for_job_conclusion.return_value = True

        params = {
            "symbol": "BTCUSDT",
            "strategy": "MovingAverage",
            "params": {"sma": 30},
            "candle_size": "1h",
            "exchange": "Binance",
            "retry": 0
        }

        res = trigger_signal(**params)

        assert res is expected_value
