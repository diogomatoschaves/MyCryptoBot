import pytest

from execution.service.cron_jobs.save_pipelines_snapshot import save_portfolio_value_snapshot, save_pipeline_snapshot
from execution.tests.setup.fixtures.external_modules import binance_handler_market_data_factory
from shared.utils.tests.fixtures.models import *


def inject_fixture(mock_name, method):
    globals()[f"{mock_name}"] = binance_handler_market_data_factory(method)


METHODS = [
    ("init_session", "_init_session"),
    ("ping", "ping"),
    ("futures_symbol_ticker", "futures_symbol_ticker"),
    ("futures_account_balance", "futures_account_balance"),
    ("futures_position_information", "futures_position_information"),
    ("futures_account", "futures_account"),
]

for method in METHODS:
    inject_fixture(*method)


@pytest.fixture
def test_mock_setup(
    create_exchange,
    ping,
    init_session,
    futures_symbol_ticker,
    futures_account_balance,
    futures_position_information,
    futures_account
):
    return


class TestCronJobs:

    @pytest.mark.parametrize(
        "pipelines,response",
        [
            pytest.param(
                [2, 11],
                {"portfolio_timeseries": 4, "values": [85, 100030]},
                id="pipelines=[2, 11]",
            ),
        ],
    )
    def test_save_portfolio_value_snapshot(
        self,
        pipelines,
        response,
        test_mock_setup,
        create_open_position,
        create_open_position_paper_trading_pipeline,
    ):
        save_portfolio_value_snapshot()

        assert PortfolioTimeSeries.objects.count() == response["portfolio_timeseries"]

        for i, pipeline in enumerate(pipelines):
            entries = PortfolioTimeSeries.objects.filter(pipeline_id=pipeline).last()
            assert entries.value == response["values"][i]

    @pytest.mark.parametrize(
        "pipelines,response",
        [
            pytest.param(
                [],
                0,
                id="no_pipeline_id",
            ),
        ],
    )
    def test_save_portfolio_value_snapshot_no_open_positions(
        self,
        pipelines,
        response,
        test_mock_setup,
    ):
        save_portfolio_value_snapshot()

        assert PortfolioTimeSeries.objects.count() == response

    @pytest.mark.parametrize(
        "pipeline,unrealized_profit",
        [
            pytest.param(
                2,
                0,
                id="pipeline_id=2-unrealized_profit=0",
            ),
            pytest.param(
                2,
                -15,
                id="pipeline_id=2-unrealized_profit=-15",
            ),
            pytest.param(
                11,
                0,
                id="pipeline_id=11-unrealized_profit=0",
            ),
            pytest.param(
                11,
                50,
                id="pipeline_id=11-unrealized_profit=50",
            ),
        ],
    )
    def test_save_pipeline_snapshot(
        self,
        pipeline,
        unrealized_profit,
        create_open_position,
        create_open_position_paper_trading_pipeline,
        test_mock_setup,
    ):
        save_pipeline_snapshot(pipeline, unrealized_profit)

        assert PortfolioTimeSeries.objects.count() == 1

        entry = PortfolioTimeSeries.objects.filter(pipeline_id=pipeline).last()

        assert entry.pipeline.id == pipeline
        assert entry.value == entry.pipeline.current_equity + unrealized_profit
