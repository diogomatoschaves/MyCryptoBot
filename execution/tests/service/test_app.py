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
        ["start_symbol_trading", "stop_symbol_trading", "execute_order/binance"],
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

    @pytest.mark.parametrize("route", ["start_symbol_trading", "stop_symbol_trading"])
    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "exchange": "Binance",
                },
                Responses.SYMBOL_REQUIRED,
                id="SYMBOL_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTC",
                    "exchange": "Binance",
                },
                Responses.SYMBOL_INVALID("BTC"),
                id="SYMBOL_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                },
                Responses.EXCHANGE_REQUIRED,
                id="EXCHANGE_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "exchange": "Coinbase",
                },
                Responses.EXCHANGE_INVALID("Coinbase"),
                id="EXCHANGE_INVALID",
            ),
        ],
    )
    def test_invalid_input(
        self,
        route,
        params,
        expected_value,
        mock_binance_trader_success,
        client,
        exchange_data,
    ):
        res = client.post(route, json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "params,route,expected_value",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "exchange": "Binance",
                },
                "start_symbol_trading",
                Responses.TRADING_SYMBOL_NO_ACCOUNT("BTCUSDT"),
                id="TRADING_SYMBOL_NO_ACCOUNT",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "exchange": "Binance",
                },
                "stop_symbol_trading",
                Responses.TRADING_SYMBOL_NOT_ACTIVE("BTCUSDT"),
                id="TRADING_SYMBOL_NOT_ACTIVE",
            ),
        ],
    )
    def test_binance_trader_fail(
        self,
        route,
        params,
        expected_value,
        mock_binance_trader_fail,
        client,
        exchange_data,
    ):
        res = client.post(route, json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "params,exchange,expected_value",
        [
            pytest.param(
                {
                    "signal": 1,
                },
                "binance",
                Responses.SYMBOL_REQUIRED,
                id="SYMBOL_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTC",
                    "signal": 10,
                },
                "binance",
                Responses.SYMBOL_INVALID("BTC"),
                id="SYMBOL_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                },
                "binance",
                Responses.SIGNAL_REQUIRED,
                id="SIGNAL_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "signal": 10,
                },
                "binance",
                Responses.SIGNAL_INVALID(10),
                id="SIGNAL_INVALID",
            ),
            pytest.param(
                {"symbol": "BTCUSDT", "signal": 1},
                "coinbase",
                Responses.EXCHANGE_INVALID("coinbase"),
                id="EXCHANGE_INVALID",
            ),
            pytest.param(
                {"symbol": "BTCUSDT", "signal": 1},
                "binance",
                Responses.ORDER_EXECUTION_SUCCESS("BTCUSDT"),
                id="ORDER_EXECUTION_SUCCESS",
            ),
        ],
    )
    def test_binance_execute_order_responses(
        self,
        exchange,
        params,
        expected_value,
        mock_binance_trader_success,
        client,
        exchange_data,
    ):
        res = client.post(f"/execute_order/{exchange}", json=params)

        assert res.json == expected_value
