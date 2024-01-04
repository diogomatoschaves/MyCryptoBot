import pytest

from django.db import InterfaceError
from flask import jsonify

from data.tests.setup.test_data.sample_data import resources_response, trades_response

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from data.tests.setup.fixtures.app import *
    from data.tests.setup.fixtures.internal_modules import *
    from data.tests.setup.fixtures.external_modules import *
    from data.service.helpers.responses import Responses

from database.model.models import Pipeline, Strategy, Trade
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.fixtures.external_modules import mock_jwt_required, spy_sys_exit, mock_sys_exit

API_PREFIX = '/api'


class TestDashboardService:

    @pytest.mark.parametrize(
        "route,method",
        [
            pytest.param(
                f'{API_PREFIX}/resources',
                'post',
                id="resources_post",
            ),
            pytest.param(
                f'{API_PREFIX}/resources',
                'put',
                id="resources_put",
            ),
            pytest.param(
                f'{API_PREFIX}/resources',
                'delete',
                id="resources_delete",
            ),
            pytest.param(
                f'{API_PREFIX}/resources',
                'post',
                id="resources_post",
            ),
            pytest.param(
                f'{API_PREFIX}/trades',
                'post',
                id="trades_post",
            ),
            pytest.param(
                f'{API_PREFIX}/trades',
                'put',
                id="trades_put",
            ),
            pytest.param(
                f'{API_PREFIX}/trades',
                'delete',
                id="trades_delete",
            ),
            pytest.param(
                f'{API_PREFIX}/pipelines',
                'post',
                id="pipelines_post",
            ),
            pytest.param(
                f'{API_PREFIX}/positions',
                'post',
                id="positions_post",
            ),
            pytest.param(
                f'{API_PREFIX}/positions',
                'put',
                id="positions_put",
            ),
            pytest.param(
                f'{API_PREFIX}/positions',
                'delete',
                id="positions_delete",
            ),
            pytest.param(
                f'{API_PREFIX}/trades-metrics',
                'post',
                id="trades-metrics_post",
            ),
            pytest.param(
                f'{API_PREFIX}/trades-metrics',
                'put',
                id="trades-metrics_put",
            ),
            pytest.param(
                f'{API_PREFIX}/trades-metrics',
                'delete',
                id="trades-metrics_delete",
            ),
            pytest.param(
                f'{API_PREFIX}/pipelines-metrics',
                'post',
                id="pipelines-metrics_post",
            ),
            pytest.param(
                f'{API_PREFIX}/pipelines-metrics',
                'put',
                id="pipelines-metrics_put",
            ),
            pytest.param(
                f'{API_PREFIX}/pipelines-metrics',
                'delete',
                id="pipelines-metrics_delete",
            ),
            pytest.param(
                f'{API_PREFIX}/pipeline-equity',
                'post',
                id="pipeline-equity_post",
            ),
            pytest.param(
                f'{API_PREFIX}/pipeline-equity',
                'put',
                id="pipeline-equity_put",
            ),
            pytest.param(
                f'{API_PREFIX}/pipeline-equity',
                'delete',
                id="pipeline-equity_delete",
            ),
            pytest.param(
                f'{API_PREFIX}/pipelines-pnl',
                'post',
                id="pipelines-pnl_post",
            ),
            pytest.param(
                f'{API_PREFIX}/pipelines-pnl',
                'put',
                id="pipelines-pnl_put",
            ),
            pytest.param(
                f'{API_PREFIX}/pipelines-pnl',
                'delete',
                id="pipelines-pnl_delete",
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
        "extra_url,response",
        [
            pytest.param(
                '',
                resources_response,
                id="resources-base_case",
            ),
            pytest.param(
                '/strategies,candleSizes,exchanges,symbols',
                resources_response,
                id="resources-all",
            ),
            pytest.param(
                '/strategies',
                {key: value for key,value in resources_response.items() if key == 'strategies'},
                id="resources-strategies",
            ),
            pytest.param(
                '/candleSizes',
                {key: value for key, value in resources_response.items() if key == 'candleSizes'},
                id="resources-candleSizes",
            ),
            pytest.param(
                '/symbols',
                {key: value for key, value in resources_response.items() if key == 'symbols'},
                id="resources-symbols",
            ),
            pytest.param(
                '/exchanges',
                {key: value for key, value in resources_response.items() if key == 'exchanges'},
                id="resources-exchanges",
            ),
            pytest.param(
                '/exchanges,symbols',
                {key: value for key, value in resources_response.items() if key in ['exchanges', 'symbols']},
                id="resources-exchanges,symbols",
            ),
        ],
    )
    def test_get_resources_endpoint(
        self,
        extra_url,
        response,
        client,
        create_symbol,
        create_exchange,
        mock_get_strategies_dashboard
    ):

        res = client.get(f'{API_PREFIX}/resources{extra_url}')

        assert res.json == response

    @pytest.mark.parametrize(
        "extra_url,included_trades",
        [
            pytest.param(
                '',
                [3, 2, 1],
                id="trades-base_case",
            ),
            pytest.param(
                '/5',
                [3, 2, 1],
                id="trades-page_with_no_trades",
            ),
            pytest.param(
                '?pipelineId=1',
                [1],
                id="trades-specific_pipeline_1",
            ),
            pytest.param(
                '/1?pipelineId=1',
                [1],
                id="trades-specific_pipeline-with_page",
            ),
            pytest.param(
                '?pipelineId=2',
                [3, 2],
                id="trades-specific_pipeline_2",
            ),
        ],
    )
    def test_get_trades_endpoint(
        self,
        extra_url,
        included_trades,
        client,
        create_trades
    ):
        res = client.get(f'{API_PREFIX}/trades{extra_url}')

        trades = [trade.as_json() for trade in Trade.objects.all().order_by('-open_time') if trade.id in included_trades]

        response = {"trades": trades}

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "extra_url,included_positions",
        [
            pytest.param(
                '',
                [1, 2],
                id="positions-base_case",
            ),
            pytest.param(
                '/5',
                [1, 2],
                id="positions-page_with_no_positions",
            ),
        ],
    )
    def test_get_positions_endpoint(
        self,
        extra_url,
        included_positions,
        client,
        create_neutral_open_inactive_position
    ):
        res = client.get(f'{API_PREFIX}/positions{extra_url}')

        positions = [position.as_json() for position in Position.objects.all() if
                  position.pipeline.active and position.pipeline.id in included_positions]

        response = {"positions": positions}

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "extra_url,get_pipelines",
        [
            pytest.param(
                '',
                lambda: [pipeline.as_json() for pipeline in
                         Pipeline.objects.filter(deleted=False).order_by('-last_entry')],
                id="pipelines-get-base_case",
            ),
            pytest.param(
                '/5',
                lambda: [pipeline.as_json() for pipeline in
                         Pipeline.objects.filter(deleted=False).order_by('-last_entry')],
                id="pipelines-get-page_with_no_pipelines",
            ),
            pytest.param(
                '/ijf',
                lambda: [],
                id="pipelines-get-page_invalid",
            ),
            pytest.param(
                '?pipelineId=1',
                lambda: [Pipeline.objects.get(id=1).as_json()],
                id="pipelines-get-with_pipelineId",
            ),
            pytest.param(
                '?pipelineId=10',
                lambda: [pipeline.as_json() for pipeline in
                         Pipeline.objects.filter(deleted=False).order_by('-last_entry')],
                id="pipelines-get-with_invalid_pipelineId",
            ),
        ],
    )
    def test_get_pipelines_endpoint(
        self,
        extra_url,
        get_pipelines,
        client,
        mock_get_strategies_dashboard,
        create_all_pipelines
    ):
        res = client.get(f'{API_PREFIX}/pipelines{extra_url}')

        response = {
            "message": "The request was successful.",
            "success": True,
            "pipelines": get_pipelines()
        }

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "extra_url,pipeline_id,response",
        [
            pytest.param(
                '',
                None,
                {"message": "The requested trading bot was not found", "success": False},
                id="pipelines-delete-base_case",
            ),
            pytest.param(
                '?pipelineId=1',
                1,
                {"message": "The trading bot was deleted", "success": True},
                id="pipelines-delete-existing_pipeline",
            ),
            pytest.param(
                '?pipelineId=100',
                100,
                {"message": "The requested trading bot was not found", "success": False},
                id="pipelines-delete-non_existent_pipeline",
            ),
        ],
    )
    def test_delete_pipelines_endpoint(
        self,
        extra_url,
        pipeline_id,
        response,
        client,
        mock_get_strategies_dashboard,
        create_all_pipelines
    ):
        res = client.delete(f'{API_PREFIX}/pipelines{extra_url}')

        if Pipeline.objects.filter(id=pipeline_id).exists():
            assert Pipeline.objects.get(id=pipeline_id).deleted is True

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "extra_url,params,response",
        [
            pytest.param(
                '',
                {
                    "color": "purple",
                    "name": "Hello World",
                    "symbol": "BTCUSDT",
                    "strategy": [{"name": "MovingAverage", "params": {"ma": 30}}],
                    "candleSize": "1h",
                    "exchanges": "Binance",
                    "leverage": 3,
                    "equity": 1000
                },
                {"message": "The requested trading bot was not found", "success": False},
                id="pipelines-put-base_case"
            ),
            pytest.param(
                '?pipelineId=1',
                {
                    "color": "purple",
                    "name": "New pipeline",
                    "symbol": "BTCUSDT",
                    "strategy": [{"name": "MovingAverage", "params": {"ma": 30}}],
                    "candleSize": "1h",
                    "exchanges": "Binance",
                    "leverage": 3,
                    "equity": 1000
                },
                {
                    "message": "The trading bot was updated successfully.",
                    "success": True,
                    "pipeline": 1
                },
                id="pipelines-put-correct_pipeline&input",
            ),
            pytest.param(
                '?pipelineId=100',
                {
                    "color": "purple",
                    "name": "New pipeline",
                    "symbol": "BTCUSDT",
                    "strategy": [{"name": "MovingAverage", "params": {"ma": 30}}],
                    "candleSize": "1h",
                    "exchanges": "Binance",
                    "leverage": 3,
                    "equity": 1000
                },
                {"message": "The requested trading bot was not found", "success": False},
                id="pipelines-put-non_existent_pipeline",
            ),
        ],
    )
    def test_put_pipelines_endpoint(
        self,
        extra_url,
        params,
        response,
        client,
        mock_get_strategies_dashboard,
        create_all_pipelines
    ):
        res = client.put(f'{API_PREFIX}/pipelines{extra_url}', json=params)

        if response["success"]:
            response["pipeline"] = Pipeline.objects.get(id=response["pipeline"]).as_json()

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "extra_url,response",
        [
            pytest.param(
                '',
                {
                    'avgTradeDuration': 300000.0,
                    'bestTrade': 0.00212,
                    'losingTrades': 0,
                    'maxTradeDuration': 300000.0,
                    'numberTrades': 3,
                    'tradesCount': [{'name': 'BTCUSDT', 'value': 3}],
                    'winningTrades': 3,
                    'worstTrade': 0.00072
                },
                id="trades_metrics-base_case",
            ),
            pytest.param(
                '?pipelineId=1',
                {
                    "avgTradeDuration": 300000.0,
                    "bestTrade": 0.00173,
                    "losingTrades": 0,
                    "maxTradeDuration": 300000.0,
                    "numberTrades": 1,
                    "winningTrades": 1,
                    "worstTrade": 0.00173,
                },
                id="trades_metrics-existing_pipeline_1",
            ),
            pytest.param(
                '?pipelineId=2',
                {
                    "avgTradeDuration": 300000.0,
                    "bestTrade": 0.00212,
                    "losingTrades": 0,
                    "maxTradeDuration": 300000.0,
                    "numberTrades": 2,
                    "winningTrades": 2,
                    "worstTrade": 0.00072,
                },
                id="trades_metrics-existing_pipeline_2",
            ),
            pytest.param(
                '?pipelineId=10',
                {
                    'avgTradeDuration': 300000.0,
                    'bestTrade': 0.00212,
                    'losingTrades': 0,
                    'maxTradeDuration': 300000.0,
                    'numberTrades': 3,
                    'tradesCount': [{'name': 'BTCUSDT', 'value': 3}],
                    'winningTrades': 3,
                    'worstTrade': 0.00072
                },
                id="trades_metrics-non_existent_pipeline",
            ),
        ],
    )
    def test_trades_metrics(
        self,
        extra_url,
        response,
        client,
        create_trades
    ):
        res = client.get(f'{API_PREFIX}/trades-metrics{extra_url}')

        print(res.json)

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "response",
        [
            pytest.param(
                {
                    "activePipelines": 2,
                    "bestWinRate": {
                        "active": True,
                        "balance": 0.0,
                        "candleSize": "1h",
                        "color": "purple",
                        "equity": 5000.0,
                        "exchange": "binance",
                        "id": 1,
                        "leverage": 1,
                        "name": "Hello World",
                        "numberTrades": 2,
                        "openTime": "2023-10-01T21:00:00+00:00",
                        "paperTrading": False,
                        "strategy": [
                            {"name": "MovingAverage", "params": {"ma": 4}},
                            {"name": "Momentum", "params": {"window": 6}},
                        ],
                        "symbol": "BTCUSDT",
                        "units": 0.3,
                        "winRate": 1.0,
                    },
                    "mostTrades": {
                        "active": True,
                        "balance": 1000.0,
                        "candleSize": "1h",
                        "color": "purple",
                        "equity": 100.0,
                        "exchange": "binance",
                        "id": 2,
                        "leverage": 10,
                        "name": "Hello World",
                        "numberTrades": 2,
                        "openTime": "2023-10-01T21:00:00+00:00",
                        "paperTrading": False,
                        "strategy": [
                            {"name": "MovingAverage", "params": {"ma": 4}},
                            {"name": "Momentum", "params": {"window": 6}},
                        ],
                        "symbol": "BTCUSDT",
                        "totalTrades": 2,
                        "units": 0.0,
                    },
                    "totalPipelines": 2,
                },
                id="pipelines_metrics",
            ),
        ],
    )
    def test_pipelines_metrics(
        self,
        response,
        client,
        create_pipeline,
        create_pipeline_2,
        create_trades
    ):
        res = client.get(f'{API_PREFIX}/pipelines-metrics')

        print(res.json)

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "extra_url,response",
        [
            pytest.param(
                '?timeFrame=100h',
                {"success": False, "message": "The provided time frame is not valid."},
                id="pipelines_metrics-wrong_timeframe",
            ),
            pytest.param(
                '/1?timeFrame=30m',
                {
                    "data": [
                        {"$": 1000.0, "time": 1696172400000},
                        {"$": 1010.0, "time": 1696174200000},
                        {"$": 1020.0, "time": 1696176000000},
                        {"$": 1015.0, "time": 1696177800000},
                        {"$": 1025.0, "time": 1696179600000},
                        {"$": 1030.0, "time": 1696181400000},
                    ],
                    "success": True,
                },
                id="pipelines_metrics-pipeline-30m",
            ),
            pytest.param(
                '/1?timeFrame=1d',
                {'data': [{'$': 1000.0, 'time': 1696118400000}], 'success': True},
                id="pipelines_metrics-pipeline-1d",
            ),
            pytest.param(
                '?timeFrame=1h',
                {
                    "data": {
                        "live": [
                            {"$": 1000.0, "time": 1696172400000},
                            {"$": 1020.0, "time": 1696176000000},
                            {"$": 1025.0, "time": 1696179600000},
                        ],
                        "testnet": [
                            {"$": 1000.0, "time": 1696172400000},
                            {"$": 1020.0, "time": 1696176000000},
                            {"$": 1025.0, "time": 1696179600000},
                        ],
                    },
                    "success": True,
                }
                ,
                id="pipelines_metrics-portfolio-1h",
            ),
        ],
    )
    def test_pipeline_equity(
        self,
        extra_url,
        response,
        client,
        create_trades,
        create_pipeline_timeseries,
        create_testnet_portfolio_timeseries,
        create_live_portfolio_timeseries,
    ):
        res = client.get(f'{API_PREFIX}/pipeline-equity{extra_url}')

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "extra_url,response",
        [
            pytest.param(
                '',
                {"success": False, "pipelinesPnl": {}},
                id="pipelines_pnl-unspecified",
            ),
            pytest.param(
                '/1',
                {'pipelinesPnl': {'1': {'pnl': 50.0, 'profit': 2500.0}}, 'success': True},
                id="pipelines_pnl-pipeline_1",
            ),
            pytest.param(
                '/2',
                {'pipelinesPnl': {'2': {'pnl': 0.0, 'profit': 0.0}}, 'success': True},
                id="pipelines_pnl-pipeline_2",
            ),
            pytest.param(
                '/3',
                {'pipelinesPnl': {'3': {'pnl': 100.0, 'profit': 500.0}}, 'success': True},
                id="pipelines_pnl-pipeline_3",
            ),
            pytest.param(
                '/9',
                {'pipelinesPnl': {}, 'success': True},
                id="pipelines_pnl-pipeline_no_equity",
            ),
            pytest.param(
                '/10',
                {'pipelinesPnl': {}, 'success': True},
                id="pipelines_pnl-pipeline_unsuccessful_price",
            ),
            pytest.param(
                '/1,2,3',
                {'pipelinesPnl': {'1': {'pnl': 50.0, 'profit': 2500.0}, '2': {'pnl': 0.0, 'profit': 0.0}, '3': {'pnl': 100.0, 'profit': 500.0}}, 'success': True},
                id="pipelines_pnl-pipeline_1,2,3",
            ),
        ],
    )
    def test_pipeline_pnl(
        self,
        extra_url,
        response,
        client,
        create_trades,
        create_trades_2,
        create_pipeline_no_equity,
        create_pipeline_BNBBTC,
        mock_get_price
    ):
        res = client.get(f'{API_PREFIX}/pipelines-pnl{extra_url}')

        print(res.json)

        assert res.json == jsonify(response).json
