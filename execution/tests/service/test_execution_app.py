import pytest

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from execution.service.helpers.responses import Responses
    from execution.tests.setup.fixtures.app import *
    from execution.tests.setup.fixtures.external_modules import *
    from execution.tests.setup.fixtures.internal_modules import *

from shared.utils.exceptions import NoSuchPipeline
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.fixtures.external_modules import mock_jwt_required


def inject_fixture(mock_name, method):
    globals()[f"{mock_name}"] = binance_handler_execution_app_factory(method)


METHODS = [
    ("init_session", "_init_session"),
    ("ping", "ping"),
    ("futures_change_leverage", "futures_change_leverage"),
    ("futures_create_order", "futures_create_order"),
    ("futures_account_balance", "futures_account_balance"),
    ("futures_position_information", "futures_position_information"),
]


for method in METHODS:
    inject_fixture(*method)


@pytest.fixture
def test_mock_setup(
    mocker,
    ping,
    init_session,
    futures_change_leverage,
    futures_create_order,
    futures_account_balance,
    futures_position_information
):
    return


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
        res = getattr(client, method)(route)

        assert res.status_code == 405

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 1,
                    "binance_account_type": "futures",
                },
                Responses.SYMBOL_ALREADY_TRADED('BTCUSDT is already being traded.'),
                id="SymbolAlreadyTraded-FUTURES",
            ),
            pytest.param(
                {
                    "pipeline_id": 2
                },
                Responses.NO_SUCH_PIPELINE("Pipeline 2 was not found."),
                id="NO_SUCH_PIPELINE",
            ),
        ],
    )
    def test_binance_trader_fail_start(
        self,
        params,
        expected_value,
        client,
        mock_binance_futures_trader_fail,
        exchange_data,
        create_pipeline,
        create_inactive_pipeline,
    ):
        res = client.post("start_symbol_trading", json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 9
                },
                Responses.EQUITY_REQUIRED("Parameter 'equity' is required."),
                id="EQUITY_REQUIRED",
            ),
            pytest.param(
                {
                    "pipeline_id": 13
                },
                Responses.INSUFFICIENT_BALANCE('Insufficient balance for starting pipeline. '
                                               '11000.0 USDT is required and current balance is 10000.0 USDT.'),
                id="INSUFFICIENT_BALANCE",
            ),
        ],
    )
    def test_start_pipeline_error_handling(
        self,
        params,
        expected_value,
        client,
        test_mock_setup,
        exchange_data,
        create_pipeline_no_equity,
        create_pipeline_with_current_equity,
    ):
        res = client.post("start_symbol_trading", json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 1,
                },
                Responses.SYMBOL_NOT_BEING_TRADED('BTCUSDT is not being traded.'),
                id="SymbolNotBeingTraded",
            ),
            pytest.param(
                {
                    "pipeline_id": 2
                },
                Responses.NO_SUCH_PIPELINE("Pipeline 2 was not found."),
                id="NO_SUCH_PIPELINE",
            ),
        ],
    )
    def test_binance_trader_fail_stop(
        self,
        params,
        expected_value,
        mock_binance_futures_trader_fail,
        client,
        exchange_data,
        create_pipeline,
        create_inactive_pipeline,
    ):
        res = client.post("stop_symbol_trading", json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 3
                },
                Responses.PIPELINE_NOT_ACTIVE('Pipeline 3 is not active.'),
                id="TRADING_SYMBOL_NOT_ACTIVE",
            ),
            pytest.param(
                {
                    "pipeline_id": 3,
                    "force": True
                },
                Responses.TRADING_SYMBOL_STOP("BTCUSDT"),
                id="TRADING_SYMBOL_NOT_ACTIVE-force",
            ),
        ],
    )
    def test_binance_trader_fail_stop_pipeline_inactive(
        self,
        params,
        expected_value,
        mock_binance_futures_trader_fail_pipeline_inactive,
        client,
        exchange_data,
        create_pipeline,
        create_inactive_pipeline,
    ):
        res = client.post("stop_symbol_trading", json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "route,params,expected_value",
        [
            pytest.param(
                "start_symbol_trading",
                {
                    "pipeline_id": 1,
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
        mock_binance_futures_trader_success,
        client,
        exchange_data,
        create_pipeline,
    ):

        res = client.post(route, json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "route,params,expected_value",
        [
            pytest.param(
                "start_symbol_trading",
                {
                    "pipeline_id": 1,
                },
                Responses.TRADING_SYMBOL_START("BTCUSDT"),
                id="START_SYMBOL_TRADING_VALID-no_mock",
            ),
            pytest.param(
                "stop_symbol_trading",
                {
                    "pipeline_id": 1,
                    "force": True,
                },
                Responses.TRADING_SYMBOL_STOP("BTCUSDT"),
                id="STOP_SYMBOL_TRADING_VALID-no_mock-Force",
            ),
            pytest.param(
                "stop_symbol_trading",
                {
                    "force": True,
                },
                Responses.NO_SUCH_PIPELINE('Pipeline None was not found.'),
                id="STOP_SYMBOL_TRADING_VALID-no_mock-missing_params",
            ),
            pytest.param(
                "stop_symbol_trading",
                {
                    "paper_trading": True,
                    "force": True,
                },
                Responses.NO_SUCH_PIPELINE('Pipeline None was not found.'),
                id="STOP_SYMBOL_TRADING_VALID-no_mock-no_symbol",
            ),
            pytest.param(
                "stop_symbol_trading",
                {
                    "symbol": "BTCUSDT",
                    "force": True,
                },
                Responses.NO_SUCH_PIPELINE('Pipeline None was not found.'),
                id="STOP_SYMBOL_TRADING_VALID-no_mock-no_paper_trading",
            ),
            pytest.param(
                "stop_symbol_trading",
                {
                    "symbol": "BTCUSDT",
                    "paper_trading": True,
                    "force": True,
                },
                Responses.TRADING_SYMBOL_STOP("BTCUSDT"),
                id="STOP_SYMBOL_TRADING_VALID-no_mock-no_paper_trading",
            ),
        ],
    )
    def test_valid_input_no_mock(
        self,
        route,
        params,
        test_mock_setup,
        expected_value,
        client,
        exchange_data,
        create_pipeline,
    ):
        res = client.post(route, json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 2,
                    "signal": 1
                },
                Responses.NO_SUCH_PIPELINE("Pipeline 2 was not found."),
                id="NO_SUCH_PIPELINE",
            ),
            pytest.param(
                {
                    "pipeline_id": 3,
                    "signal": 1,
                },
                Responses.PIPELINE_NOT_ACTIVE('Pipeline 3 is not active.'),
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
                Responses.SIGNAL_INVALID('abc is not a valid signal.'),
                id="SIGNAL_INVALID",
            ),
            pytest.param(
                {
                    "pipeline_id": 1,
                },
                Responses.SIGNAL_REQUIRED("Parameter 'signal' is required."),
                id="SIGNAL_REQUIRED",
            ),
        ],
    )
    def test_binance_execute_order_responses(
        self,
        params,
        expected_value,
        mock_binance_futures_trader_success,
        client,
        exchange_data,
        create_pipeline,
        create_inactive_pipeline,
    ):
        res = client.post(f"/execute_order", json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 1,
                    "signal": 1
                },
                Responses.API_ERROR("BTCUSDT", "Precision is over the maximum defined for this asset."),
                id="API_ERROR-execute_order",
            ),
        ]
    )
    def test_failed_execute_order(
        self,
        params,
        expected_value,
        mock_binance_futures_trader_raise_exception_trade,
        client,
        exchange_data,
        create_pipeline,
        create_inactive_pipeline,
    ):

        res = client.post(f"/execute_order", json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "endpoint,params,expected_value",
        [
            pytest.param(
                "/execute_order",
                {
                    "pipeline_id": 1,
                    "signal": 1
                },
                Responses.NEGATIVE_EQUITY('Pipeline 1 has reached negative equity.'),
                id="NEGATIVE_EQUITY-execute-order",
            ),
            pytest.param(
                "/stop_symbol_trading",
                {
                    "pipeline_id": 1,
                    "signal": 1
                },
                Responses.NEGATIVE_EQUITY('Pipeline 1 has reached negative equity.'),
                id="NEGATIVE_EQUITY-stop_symbol_trading",
            ),
        ]
    )
    def test_failed_execute_order_negative_equity(
        self,
        endpoint,
        params,
        expected_value,
        mock_binance_futures_trader_raise_negative_equity_error,
        client,
        exchange_data,
        create_pipeline,
        create_inactive_pipeline,
    ):

        res = client.post(endpoint, json=params)

        assert res.json == expected_value

    @pytest.mark.parametrize(
        "route,params,expected_value",
        [
            pytest.param(
                "start_symbol_trading",
                {
                    "pipeline_id": 1,
                    "equity": 2
                },
                Responses.API_ERROR("BTCUSDT", "ReduceOnly Order is rejected."),
                id="API_ERROR-start_symbol_trading",
            ),
            pytest.param(
                "stop_symbol_trading",
                {
                    "pipeline_id": 1,
                },
                Responses.API_ERROR("BTCUSDT", "ReduceOnly Order is rejected."),
                id="API_ERROR-stop_symbol_trading",
            ),
        ]
    )
    def test_failed_start_stop_symbol_trading(
        self,
        route,
        params,
        expected_value,
        mock_binance_futures_trader_raise_exception_start_stop,
        client,
    ):
        res = client.post(f"{route}", json=params)

        assert res.json == expected_value

    def test_failed_leverage_setting(
        self,
        mock_binance_futures_trader_raise_leverage_setting_fail,
        create_pipeline,
        client,
    ):
        res = client.post(f"start_symbol_trading", json={"pipeline_id": 1})

        assert res.json == Responses.LEVERAGE_SETTING_FAILURE("Failed to set leverage. ")
