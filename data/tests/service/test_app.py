import json

from data.service.helpers.responses import Responses
from data.tests.setup.fixtures.internal_modules import *
from data.tests.setup.fixtures.external_modules import *
from data.tests.setup.fixtures.app import *
from database.model.models import Pipeline
from shared.utils.tests.fixtures.models import *


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
        "input_params,response,get_response",
        [
            pytest.param(
                {
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "SYMBOL_REQUIRED",
                lambda response: response,
                id="SYMBOL_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                },
                "EXCHANGE_REQUIRED",
                lambda response: response,
                id="EXCHANGE_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "exchanges": "Binance"
                },
                "CANDLE_SIZE_REQUIRED",
                lambda response: response,
                id="CANDLE_SIZE_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "STRATEGY_REQUIRED",
                lambda response: response,
                id="STRATEGY_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "candleSize": "1h",
                    "exchanges": "Binance"
                },
                "PARAMS_REQUIRED",
                lambda response: response("ma"),
                id="PARAMS_REQUIRED",
            ),
        ],
    )
    def test_start_bot_required_input_response(
        self,
        input_params,
        response,
        get_response,
        client,
        mock_settings_env_vars,
        mock_redis_connection,
        mock_get_strategies,
        create_exchange,
        create_assets,
        create_symbol
    ):
        """
        GIVEN some input params
        WHEN one input_parameter is missing
        THEN the corresponding response will be sent

        """

        res = client.put('/start_bot', json=input_params)

        assert res.json == get_response(getattr(Responses, response))

    @pytest.mark.parametrize(
        "input_params,response,get_param",
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
                lambda input_params: input_params["symbol"],
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
                lambda input_params: input_params["exchanges"],
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
                lambda input_params: input_params["candleSize"],
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
                lambda input_params: input_params["strategy"],
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
                lambda input_params: "sma",
                id="PARAMS_INVALID",
            ),
        ],
    )
    def test_start_bot_invalid_input_response(
        self,
        input_params,
        response,
        get_param,
        client,
        mock_settings_env_vars,
        mock_redis_connection,
        mock_get_strategies,
        create_exchange,
        create_assets,
        create_symbol
    ):
        """
        GIVEN some input params
        WHEN one input_parameter is invalid
        THEN the corresponding response will be sent

        """

        res = client.put('/start_bot', json=input_params)

        assert res.json == getattr(Responses, response)(get_param(input_params))

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance",
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
        mock_settings_env_vars,
        mock_redis_connection,
        mock_get_strategies,
        create_exchange,
        create_assets,
        create_symbol,
        create_pipeline,
    ):
        """
        GIVEN some input params
        WHEN one pipeline job is present
        THEN the corresponding response will be sent

        """

        res = client.put('/start_bot', json=params)

        assert res.json == getattr(Responses, response)(1)

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"ma": 30},
                    "candleSize": "1h",
                    "exchanges": "Binance"
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
        mock_start_stop_symbol_trading_success_true,
        client,
        mock_settings_env_vars,
        mock_redis_connection,
        mock_get_strategies,
        mock_binance_handler_start_data_ingestion,
        mock_executor_submit,
        binance_handler_instances_spy_start_bot,
        create_exchange,
        create_assets,
        create_symbol,
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        res = client.put('/start_bot', json=params)

        print(Pipeline.objects.all().count())

        assert res.json["response"] == getattr(Responses, response)(1)["response"]
        assert type(res.json["pipeline_id"]) == int
        assert len(binance_handler_instances_spy_start_bot) == 1

        pipeline = Pipeline.objects.last()

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
        mock_start_stop_symbol_trading_success_false,
        client,
        mock_settings_env_vars,
        mock_binance_handler_start_data_ingestion,
        mock_get_strategies,
        mock_redis_connection,
        create_exchange,
        create_assets,
        create_symbol,
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        res = client.put('/start_bot', json=params)

        assert res.json["response"] == 'Failed'

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "pipeline_id": 1
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
        mock_settings_env_vars,
        mock_binance_handler_stop_data_ingestion,
        mock_redis_connection,
        mock_get_strategies,
        binance_handler_stop_data_ingestion_spy,
        mock_start_stop_symbol_trading_success_true,
        binance_handler_instances_spy_stop_bot,
        create_exchange,
        create_assets,
        create_symbol,
        create_pipeline
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        assert len(binance_handler_instances_spy_stop_bot) == 1

        res = client.put('/stop_bot', json=params)

        assert res.json == getattr(Responses, response)

        pipeline = Pipeline.objects.get(id=params["pipeline_id"])
        assert pipeline.active is False

        binance_handler_stop_data_ingestion_spy.assert_called()

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "pipeline_id": 1
                },
                "DATA_PIPELINE_INEXISTENT",
                id="DATA_PIPELINE_INEXISTENT",
            ),
        ],
    )
    def test_stop_bot_data_pipeline_inexistent(
        self,
        params,
        response,
        client,
        mock_settings_env_vars,
        mock_redis_connection,
        mock_get_strategies,
        create_exchange,
        create_assets,
        create_symbol,
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        res = client.put('/stop_bot', json=params)

        assert res.json == getattr(Responses, response)
