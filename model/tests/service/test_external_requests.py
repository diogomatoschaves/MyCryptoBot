from model.service.external_requests import execute_order
from model.service.helpers import EXECUTION_APP_ENDPOINTS
from model.tests.setup.fixtures.internal_modules import *
from shared.utils.tests.fixtures.external_modules import *


class TestModelExternalRequests:
    def test_execute_order(
        self, mock_settings_env_vars, mock_requests_post, requests_post_spy
    ):
        """
        GIVEN some params
        WHEN the method execute_order is called
        THEN the return value is equal to the expected response

        """

        params = {
            "symbol": "BTCUSDT",
            "signal": 1,
        }

        exchange = "Binance"

        res = execute_order(**{**params, "exchange": exchange})

        assert res == response
        requests_post_spy.assert_called_with(
            EXECUTION_APP_ENDPOINTS["EXECUTE_ORDER"](
                os.getenv("EXECUTION_APP_URL"), exchange
            ),
            json=params,
        )
