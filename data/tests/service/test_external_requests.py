from data.service.external_requests import generate_signal, start_stop_symbol_trading, check_job_status, get_strategies
from data.service.helpers import MODEL_APP_ENDPOINTS, EXECUTION_APP_ENDPOINTS
from data.tests.setup.fixtures.internal_modules import *
from data.tests.setup.fixtures.external_modules import *
from data.tests.setup.fixtures.app import *
from shared.utils.tests.fixtures.external_modules import *
from shared.utils.tests.fixtures.models import *


class TestDataExternalRequests:

    def test_generate_signal(
        self,
        mock_settings_env_vars,
        mock_requests_post,
        mock_redis_connection,
        requests_post_spy
    ):
        """
        GIVEN some params
        WHEN the method generate_signal is called
        THEN the return value is equal to the expected response

        """

        params = {
            "pipeline_id": 1
        }

        res = generate_signal(**params)

        assert res == response
        requests_post_spy.assert_called_with(
            MODEL_APP_ENDPOINTS["GENERATE_SIGNAL"](os.getenv("MODEL_APP_URL")),
            json=params
        )

    @pytest.mark.parametrize(
        "params,start_or_stop",
        [
            pytest.param(
                {
                    "pipeline_id": 1
                },
                "start",
                id="START_SYMBOL_TRADING",
            ),
            pytest.param(
                {
                    "pipeline_id": 1
                },
                "stop",
                id="STOP_SYMBOL_TRADING",
            ),
        ],
    )
    def test_start_stop_symbol_trading(
        self,
        params,
        start_or_stop,
        mock_settings_env_vars,
        mock_requests_post,
        requests_post_spy
    ):
        """
        GIVEN some params
        WHEN the method start_stop_symbol_trading is called
        THEN the return value is equal to the expected response

        """

        expanded_params = {
            **params,
            "start_or_stop": start_or_stop
        }

        endpoint = f"{start_or_stop.upper()}_SYMBOL_TRADING"

        res = start_stop_symbol_trading(**expanded_params)

        assert res == response
        requests_post_spy.assert_called_with(
            EXECUTION_APP_ENDPOINTS[endpoint](os.getenv("EXECUTION_APP_URL")),
            json=params
        )

    def test_check_job_status(
        self,
        mock_settings_env_vars,
        mock_requests_get,
        requests_get_spy
    ):
        """
        GIVEN some params
        WHEN the method start_stop_symbol_trading is called
        THEN the return value is equal to the expected response

        """

        job_id = 'abcdef'

        res = check_job_status(job_id)

        assert res == response
        requests_get_spy.assert_called_with(
            MODEL_APP_ENDPOINTS["CHECK_JOB"](os.getenv("MODEL_APP_URL"), job_id),
        )

    def test_get_strategies(
        self,
        mock_settings_env_vars,
        mock_requests_get,
        mock_redis_connection,
        requests_get_spy
    ):
        """
        GIVEN some params
        WHEN the method generate_signal is called
        THEN the return value is equal to the expected response

        """

        res = get_strategies()

        assert res == response
        requests_get_spy.assert_called_with(
            MODEL_APP_ENDPOINTS["GET_STRATEGIES"](os.getenv("MODEL_APP_URL")),
        )
