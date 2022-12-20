import json

from django.db import InterfaceError

from data.service.helpers.responses import Responses
from data.tests.setup.fixtures.internal_modules import *
from data.tests.setup.fixtures.external_modules import *
from data.tests.setup.fixtures.app import *
from database.model.models import Pipeline
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.fixtures.external_modules import mock_jwt_required


class TestDataService:

    def test_index_route(self, client):

        res = client.get('/')

        assert res.data.decode(res.charset) == "I'm up!"

    @pytest.mark.parametrize(
        "route,method",
        [
            pytest.param(
                'start_bot',
                'get',
                id="start_bot_get",
            ),
            pytest.param(
                'start_bot',
                'post',
                id="start_bot_post",
            ),
            pytest.param(
                'start_bot',
                'delete',
                id="start_bot_delete",
            ),
            pytest.param(
                'stop_bot',
                'get',
                id="start_bot_delete",
            ),
            pytest.param(
                'stop_bot',
                'post',
                id="start_bot_delete",
            ),
            pytest.param(
                'stop_bot',
                'delete',
                id="start_bot_delete",
            ),
        ],
    )
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
        "input_params,response,message",
        [
            pytest.param(
                {
                    "name": "Hello World",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "SYMBOL_REQUIRED",
                'A symbol must be included in the request.',
                id="SYMBOL_REQUIRED",
            ),
            pytest.param(
                {
                    "name": "Hello World",
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                },
                "EXCHANGE_REQUIRED",
                'An exchange must be included in the request.',
                id="EXCHANGE_REQUIRED",
            ),
            pytest.param(
                {
                    "name": "Hello World",
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "exchanges": "Binance"
                },
                "CANDLE_SIZE_REQUIRED",
                'A candle size must be included in the request.',
                id="CANDLE_SIZE_REQUIRED",
            ),
            pytest.param(
                {
                    "name": "Hello World",
                    "symbol": "BTCUSDT",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "STRATEGY_REQUIRED",
                'A strategy must be included in the request.',
                id="STRATEGY_REQUIRED",
            ),
            pytest.param(
                {
                    "name": "Hello World",
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverageCrossover",
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "PARAMS_REQUIRED",
                'SMA_S, SMA_L are required parameters of the selected strategy.',
                id="PARAMS_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "NAME_REQUIRED",
                'A name must be included in the request.',
                id="NAME_REQUIRED",
            ),
        ],
    )
    def test_start_bot_required_input_response(
        self,
        input_params,
        response,
        message,
        client,
    ):
        """
        GIVEN some input params
        WHEN one input_parameter is missing
        THEN the corresponding response will be sent

        """

        res = client.put('/start_bot', json=input_params)

        assert res.json == getattr(Responses, response)(message)

    @pytest.mark.parametrize(
        "input_params,response,get_message",
        [
            pytest.param(
                {
                    "symbol": "BTC",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "SYMBOL_INVALID",
                lambda input_params: f'{input_params["symbol"]} is not a valid symbol.',
                id="SYMBOL_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Coinbase"
                },
                "EXCHANGE_INVALID",
                lambda input_params: f'{input_params["exchanges"]} is not a valid exchange.',
                id="EXCHANGE_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "efrefg",
                    "exchanges": "Binance"
                },
                "CANDLE_SIZE_INVALID",
                lambda input_params: f'{input_params["candleSize"]} is not a valid candle size.',
                id="CANDLE_SIZE_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "Average",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "STRATEGY_INVALID",
                lambda input_params: f'{input_params["strategy"]} is not a valid strategy.',
                id="STRATEGY_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30, "ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "PARAMS_INVALID",
                lambda input_params: f'sma are not valid parameters.',
                id="PARAMS_INVALID",
            ),
            pytest.param(
                {
                    "name": False,
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "NAME_INVALID",
                lambda input_params: f'{input_params["name"]} is not a valid name.',
                id="NAME_INVALID",
            ),
            pytest.param(
                {
                    "name": "TEST",
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance",
                    "leverage": "20"
                },
                "LEVERAGE_INVALID",
                lambda input_params: f'{input_params["leverage"]} is not a valid leverage.',
                id="LEVERAGE_INVALID",
            ),
        ],
    )
    def test_start_bot_invalid_input_response(
        self,
        input_params,
        response,
        get_message,
        client,
    ):
        """
        GIVEN some input params
        WHEN one input_parameter is invalid
        THEN the corresponding response will be sent

        """

        res = client.put('/start_bot', json=input_params)

        assert res.json == getattr(Responses, response)(get_message(input_params))

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "color": "purple",
                    "name": "Hello World",
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance",
                    "allocation": 100,
                    "leverage": 1
                },
                "DATA_PIPELINE_ONGOING",
                id="DATA_PIPELINE_ONGOING",
            ),
        ],
    )
    def test_start_bot_ongoing_pipeline(
        self,
        params,
        response,
        client,
        create_pipeline,
    ):
        """
        GIVEN some input params
        WHEN one pipeline job is present
        THEN the corresponding response will be sent

        """

        res = client.put('/start_bot', json=params)

        assert res.json == getattr(Responses, response)('Data pipeline 1 is already ongoing.', 1)

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "color": "purple",
                    "name": "Hello World",
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance",
                    "leverage": 3
                },
                "DATA_PIPELINE_START_OK",
                id="DATA_PIPELINE_START_OK",
            ),
        ],
    )
    def test_start_bot_new_pipeline(
        self,
        params,
        response,
        client,
        mock_start_stop_symbol_trading_success_true,
        mock_binance_handler_start_data_ingestion,
        mock_binance_threaded_websocket,
        mock_binance_websocket_start,
        mock_binance_websocket_stop,
        mock_executor_submit,
        binance_handler_instances_spy_start_bot,
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        res = client.put('/start_bot', json=params)

        pipeline = Pipeline.objects.last()

        assert res.json == getattr(Responses, response)(pipeline)
        assert len(binance_handler_instances_spy_start_bot) == 1

        assert pipeline.symbol.name == params["symbol"]
        assert pipeline.exchange.name == params["exchanges"].lower()
        assert pipeline.strategy == params["strategy"]
        assert pipeline.params == json.dumps(params["params"])
        assert pipeline.interval == params["candleSize"]

    @pytest.mark.parametrize(
        "params",
        [
            pytest.param(
                {
                    "color": "purple",
                    "name": "Hello World",
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                id="DATA_PIPELINE_FAIL_EXTERNAL_CALL",
            ),
        ],
    )
    def test_start_bot_unsuccessful_response(
        self,
        params,
        client,
        mock_start_stop_symbol_trading_success_false,
        mock_binance_handler_start_data_ingestion,
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        res = client.put('/start_bot', json=params)

        assert res.json["message"] == 'Pipeline start failed.'

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "pipelineId": 1
                },
                "DATA_PIPELINE_STOPPED",
                id="DATA_PIPELINE_STOPPED",
            ),
        ],
    )
    def test_stop_bot_data_pipeline_stopped(
        self,
        params,
        response,
        client,
        mock_binance_handler_stop_data_ingestion,
        mock_binance_threaded_websocket,
        mock_binance_websocket_start,
        mock_binance_websocket_stop,
        binance_handler_stop_data_ingestion_spy,
        mock_start_stop_symbol_trading_success_true,
        binance_handler_instances_spy_stop_bot,
        create_pipeline
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        assert len(binance_handler_instances_spy_stop_bot) == 1

        res = client.put('/stop_bot', json=params)

        pipeline = Pipeline.objects.get(id=params["pipelineId"])

        assert res.json == getattr(Responses, response)(pipeline)

        assert pipeline.active is False

        binance_handler_stop_data_ingestion_spy.assert_called()

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "pipelineId": 1
                },
                "DATA_PIPELINE_DOES_NOT_EXIST",
                id="DATA_PIPELINE_DOES_NOT_EXIST",
            ),
        ],
    )
    def test_stop_bot_data_pipeline_does_not_exist(
        self,
        params,
        response,
        client,
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        res = client.put('/stop_bot', json=params)

        assert res.json == getattr(Responses, response)(f'Data pipeline {params["pipelineId"]} does not exist.')

    def test_startup_task_existing_positions(
        self,
        client_with_open_position,
        spy_start_symbol_trading
    ):
        spy_start_symbol_trading.assert_called_once()

    def test_startup_task_no_positions(
        self,
        client,
        spy_start_symbol_trading
    ):
        spy_start_symbol_trading.assert_not_called()

    @pytest.mark.parametrize(
        "raises_error,side_effect,call_count",
        [
            pytest.param(
                True,
                get_strategies_side_effect_3_errors,
                2,
                id="3-errors|2-calls",
            ),
            pytest.param(
                True,
                get_strategies_side_effect_2_errors,
                2,
                id="2-errors|2-calls",
            ),
            pytest.param(
                False,
                get_strategies_side_effect_1_errors,
                1,
                id="1-errors|1-calls",
            ),
            pytest.param(
                False,
                get_strategies_side_effect_0_errors,
                0,
                id="0-errors|0-calls",
            ),
        ],
    )
    def test_interface_error_handling(
        self,
        raises_error,
        side_effect,
        call_count,
        client,
        mock_get_strategies_raise_exception,
        spy_db_connection
    ):

        mock_get_strategies_raise_exception.side_effect = side_effect

        if raises_error:
            with pytest.raises(InterfaceError):
                client.get('/resources/strategies')
        else:
            client.get('/resources/strategies')

        assert spy_db_connection.call_count == call_count
