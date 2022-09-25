from execution.service.helpers.responses import Responses
from execution.tests.setup.fixtures.app import *
from execution.tests.setup.fixtures.external_modules import *
from execution.tests.setup.fixtures.internal_modules import *
from shared.utils.tests.fixtures.models import *


class TestExecutionService:
    def test_index_route(self, client):

        res = client.get("/")

        assert res.data.decode(res.charset) == "I'm up!"

    @pytest.mark.parametrize(
        "route",
        ["start_symbol_trading", "stop_symbol_trading", "execute_order"],
    )
    @pytest.mark.parametrize("method", ["get", "put", "delete"])
    def test_routes_disallowed_methods(self, route, method, client):
        """
        GIVEN a method for a certain route
        WHEN the method is invalid
        THEN the status code of the response will be 405

        equivalent to eg:

        res = client.get('/start_bot')

        """

        print(route, method)

        res = getattr(client, method)(route)

        print(res.data)

        assert res.status_code == 405

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 1,
                    "binance_account_type": "margin",
                    "equity": 100
                },
                Responses.TRADING_SYMBOL_NO_ACCOUNT("BTCUSDT"),
                id="TRADING_SYMBOL_NO_ACCOUNT_MARGIN",
            ),
            pytest.param(
                {
                    "pipeline_id": 1,
                    "binance_account_type": "futures",
                    "equity": 100
                },
                Responses.TRADING_SYMBOL_NO_ACCOUNT("BTCUSDT"),
                id="TRADING_SYMBOL_NO_ACCOUNT_FUTURES",
            ),
            pytest.param(
                {
                    "pipeline_id": 1,
                },
                Responses.EQUITY_REQUIRED("BTCUSDT"),
                id="TRADING_SYMBOL_NO_EQUITY",
            ),
            pytest.param(
                {
                    "pipeline_id": 2
                },
                Responses.NO_SUCH_PIPELINE(2),
                id="NO_SUCH_PIPELINE",
            ),
            pytest.param(
                {
                    "pipeline_id": 3
                },
                Responses.PIPELINE_NOT_ACTIVE("BTCUSDT", 3),
                id="TRADING_SYMBOL_NOT_ACTIVE",
            ),
        ],
    )
    def test_binance_trader_fail_start(
        self,
        params,
        expected_value,
        mock_binance_margin_trader_fail,
        mock_binance_futures_trader_fail,
        mock_redis_connection,
        client,
        exchange_data,
        create_pipeline,
        create_inactive_pipeline
    ):
        res = client.post("start_symbol_trading", json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 1,
                    "binance_account_type": "margin",
                    "equity": 100
                },
                Responses.TRADING_SYMBOL_NO_ACCOUNT("BTCUSDT"),
                id="TRADING_SYMBOL_NO_ACCOUNT_MARGIN",
            ),
            pytest.param(
                {
                    "pipeline_id": 1,
                    "binance_account_type": "futures",
                    "equity": 100
                },
                Responses.TRADING_SYMBOL_NO_ACCOUNT("BTCUSDT"),
                id="TRADING_SYMBOL_NO_ACCOUNT_FUTURES",
            ),
            pytest.param(
                {
                    "pipeline_id": 2
                },
                Responses.NO_SUCH_PIPELINE(2),
                id="NO_SUCH_PIPELINE",
            ),
            pytest.param(
                {
                    "pipeline_id": 3
                },
                Responses.PIPELINE_NOT_ACTIVE("BTCUSDT", 3),
                id="TRADING_SYMBOL_NOT_ACTIVE",
            ),
        ],
    )
    def test_binance_trader_fail_stop(
            self,
            params,
            expected_value,
            mock_binance_margin_trader_fail,
            mock_binance_futures_trader_fail,
            mock_redis_connection,
            client,
            exchange_data,
            create_pipeline,
            create_inactive_pipeline
    ):
        res = client.post("stop_symbol_trading", json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "binance_account_type",
        [
            pytest.param(
                {"binance_account_type": "margin"},
                id="MARGIN"
            ),
            pytest.param(
                {"binance_account_type": "futures"},
                id="FUTURES"
            ),
        ],
    )
    @pytest.mark.parametrize(
        "route,params,expected_value",
        [
            pytest.param(
                "start_symbol_trading",
                {
                    "pipeline_id": 1,
                    "equity": 100
                },
                Responses.TRADING_SYMBOL_START("BTCUSDT"),
                id="START_SYMBOL_TRADING_VALID",
            ),
            pytest.param(
                "stop_symbol_trading",
                {
                    "pipeline_id": 1,
                },
                Responses.TRADING_SYMBOL_STOP("BTCUSDT"),
                id="STOP_SYMBOL_TRADING_VALID",
            ),
        ],
    )
    def test_valid_input(
        self,
        route,
        params,
        expected_value,
        binance_account_type,
        mock_binance_margin_trader_success,
        mock_binance_futures_trader_success,
        mock_redis_connection,
        client,
        exchange_data,
        create_pipeline
    ):
        payload = {
            **params,
            **binance_account_type
        }

        res = client.post(route, json=payload)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "binance_account_type",
        [
            pytest.param(
                {"binance_account_type": "margin"},
                id="MARGIN"
            ),
            pytest.param(
                {"binance_account_type": "futures"},
                id="FUTURES"
            ),
        ],
    )
    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 2,
                    "signal": 1
                },
                Responses.NO_SUCH_PIPELINE(2),
                id="NO_SUCH_PIPELINE",
            ),
            pytest.param(
                {
                    "pipeline_id": 3,
                    "signal": 1,
                },
                Responses.PIPELINE_NOT_ACTIVE("BTCUSDT", 3),
                id="TRADING_SYMBOL_NOT_ACTIVE",
            ),
            pytest.param(
                {
                    "pipeline_id": 1,
                    "signal": 1
                },
                Responses.ORDER_EXECUTION_SUCCESS("BTCUSDT"),
                id="ORDER_EXECUTION_SUCCESS",
            ),
            pytest.param(
                {
                    "pipeline_id": 1,
                    "signal": "abc"
                },
                Responses.SIGNAL_INVALID("abc"),
                id="SIGNAL_INVALID",
            ),
            pytest.param(
                {
                    "pipeline_id": 1,
                },
                Responses.SIGNAL_REQUIRED,
                id="SIGNAL_REQUIRED",
            ),
        ],
    )
    def test_binance_execute_order_responses(
        self,
        params,
        expected_value,
        binance_account_type,
        mock_binance_margin_trader_success,
        mock_binance_futures_trader_success,
        mock_redis_connection,
        client,
        exchange_data,
        create_pipeline,
        create_inactive_pipeline,
    ):

        payload = {
            **params,
            **binance_account_type
        }

        res = client.post(f"/execute_order", json=payload)

        assert res.json == expected_value
