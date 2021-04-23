import os

import pytest

from data.service.helpers.responses import Responses
from data.tests.setup.fixtures.app import *
from data.tests.setup.fixtures.models import *
from data.tests.setup.fixtures.internal_modules import *


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
        "input_params,response",
        [
            pytest.param(
                {
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                    "exchange": "Binance"
                },
                "SYMBOL_REQUIRED",
                id="SYMBOL_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                },
                "EXCHANGE_REQUIRED",
                id="EXCHANGE_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "exchange": "Binance"
                },
                "CANDLE_SIZE_REQUIRED",
                id="CANDLE_SIZE_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                    "exchange": "Binance"
                },
                "STRATEGY_REQUIRED",
                id="STRATEGY_REQUIRED",
            ),
        ],
    )
    def test_start_bot_required_input_response(
        self,
        input_params,
        response,
        client,
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

        assert res.json == getattr(Responses, response)

    @pytest.mark.parametrize(
        "input_params,response,param",
        [
            pytest.param(
                {
                    "symbol": "BTC",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                    "exchange": "Binance"
                },
                "SYMBOL_INVALID",
                "symbol",
                id="SYMBOL_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                    "exchange": "Coinbase"
                },
                "EXCHANGE_INVALID",
                "exchange",
                id="EXCHANGE_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "candle_size": "efrefg",
                    "exchange": "Binance"
                },
                "CANDLE_SIZE_INVALID",
                "candle_size",
                id="CANDLE_SIZE_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "Average",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                    "exchange": "Binance"
                },
                "STRATEGY_INVALID",
                "strategy",
                id="STRATEGY_INVALID",
            ),
        ],
    )
    def test_start_bot_invalid_input_response(
            self,
            input_params,
            response,
            param,
            client,
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

        assert res.json == getattr(Responses, response)(input_params[param])

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                    "exchange": "Binance"
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
        create_exchange,
        create_assets,
        create_symbol,
        create_job,
    ):
        """
        GIVEN some input params
        WHEN one pipeline job is present
        THEN the corresponding response will be sent

        """

        res = client.put('/start_bot', json=params)

        assert res.json == getattr(Responses, response)(params["symbol"])

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                    "exchange": "Binance"
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

        assert res.json == getattr(Responses, response)(params["symbol"])
        assert len(binance_handler_instances_spy_start_bot) == 1

    @pytest.mark.parametrize(
        "params",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "strategy": "MovingAverage",
                    "params": {"sma": 30},
                    "candle_size": "1h",
                    "exchange": "Binance"
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
        mock_binance_handler_start_data_ingestion,
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
        "input_params,response",
        [
            pytest.param(
                {
                    "exchange": "Binance"
                },
                "SYMBOL_REQUIRED",
                id="SYMBOL_REQUIRED",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                },
                "EXCHANGE_REQUIRED",
                id="EXCHANGE_REQUIRED",
            ),
        ],
    )
    def test_stop_bot_required_input_response(
            self,
            input_params,
            response,
            client,
            create_exchange,
            create_assets,
            create_symbol
    ):
        """
        GIVEN some input params
        WHEN one input_parameter is missing
        THEN the corresponding response will be sent

        """

        res = client.put('/stop_bot', json=input_params)

        assert res.json == getattr(Responses, response)

    @pytest.mark.parametrize(
        "input_params,response,param",
        [
            pytest.param(
                {
                    "symbol": "BTC",
                    "exchange": "Binance"
                },
                "SYMBOL_INVALID",
                "symbol",
                id="SYMBOL_INVALID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "exchange": "Coinbase"
                },
                "EXCHANGE_INVALID",
                "exchange",
                id="EXCHANGE_INVALID",
            ),
        ],
    )
    def test_stop_bot_invalid_input_response(
            self,
            input_params,
            response,
            param,
            client,
            create_exchange,
            create_assets,
            create_symbol
    ):
        """
        GIVEN some input params
        WHEN one input_parameter is invalid
        THEN the corresponding response will be sent

        """

        res = client.put('/stop_bot', json=input_params)

        assert res.json == getattr(Responses, response)(input_params[param])

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "exchange": "Binance"
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
        binance_handler_stop_data_ingestion_spy,
        mock_start_stop_symbol_trading_success_true,
        binance_handler_instances_spy_stop_bot,
        create_exchange,
        create_assets,
        create_symbol,
        create_job
    ):
        """
        GIVEN some input params
        WHEN everything works as expected
        THEN the corresponding response will be sent and the pipeline is started

        """

        assert len(binance_handler_instances_spy_stop_bot) == 1

        res = client.put('/stop_bot', json=params)

        assert res.json == getattr(Responses, response)(params["symbol"])
        assert Jobs.objects.count() == 0

        binance_handler_stop_data_ingestion_spy.assert_called()

    @pytest.mark.parametrize(
        "params,response",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "exchange": "Binance"
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

        assert res.json == getattr(Responses, response)(params["symbol"])
