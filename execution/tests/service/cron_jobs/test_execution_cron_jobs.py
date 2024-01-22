import pytest

from execution.service.cron_jobs.save_pipelines_snapshot import save_pipelines_snapshot
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
]

for method in METHODS:
    inject_fixture(*method)


@pytest.fixture
def test_mock_setup(
    mocker,
    create_open_position,
    create_open_position_paper_trading_pipeline,
    ping,
    init_session,
    futures_symbol_ticker,
    futures_account_balance,
    futures_position_information
):
    return


class MockBinanceInstance:

    def __init__(self, paper_trading=False):
        self.paper_trading = paper_trading

        self.current_balance = {
            "BTCUSDT": 1000
        }

        self.units = {
            "BTCUSDT": 0.1
        }


class TestCronJobs:

    @pytest.mark.parametrize(
        "pipelines,response",
        [
            pytest.param(
                [2, 11],
                {"portfolio_timeseries": 4, "values": [4100, 3500]},
                id="no_pipeline_id",
            ),
            pytest.param(
                [2],
                {"portfolio_timeseries": 1, "values": [4100]},
                id="existent_pipeline_2",
            ),
            pytest.param(
                [11],
                {"portfolio_timeseries": 1, "values": [3500]},
                id="existent_pipeline_11",
            ),
        ],
    )
    def test_save_pipelines_snapshot(
        self,
        pipelines,
        response,
        test_mock_setup,
    ):
        binance_instances = [MockBinanceInstance(), MockBinanceInstance(paper_trading=True)]

        kwargs = {}
        if len(pipelines) == 1:
            kwargs['pipeline_id'] = pipelines[0]

        save_pipelines_snapshot(binance_instances, **kwargs)

        assert PortfolioTimeSeries.objects.count() == response["portfolio_timeseries"]

        for i, pipeline in enumerate(pipelines):
            entries = PortfolioTimeSeries.objects.filter(pipeline_id=pipeline)
            assert entries[0].value == response["values"][i]
