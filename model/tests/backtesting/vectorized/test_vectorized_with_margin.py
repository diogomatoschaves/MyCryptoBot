import os

import pandas as pd
import pytest

from model.backtesting import VectorizedBacktester, IterativeBacktester
from model.strategies import MovingAverage
from model.tests.setup.fixtures.external_modules import mocked_plotly_figure_show
from model.tests.setup.test_data.sample_data import data
from shared.utils.exceptions import SymbolInvalid
from shared.utils.exceptions.leverage_invalid import LeverageInvalid
from shared.utils.tests.test_setup import get_fixtures

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path, keys=["in_margin", "out_margin"])


cum_returns = "accumulated_strategy_returns"
cum_returns_tc = "accumulated_strategy_returns_tc"
margin_ratio = "margin_ratios"


class TestVectorizedBacktesterMargin:
    @pytest.mark.parametrize(
        "leverage",
        [pytest.param(1, id="leverage=1"), pytest.param(10, id="leverage=10")],
    )
    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_run(self, leverage, fixture, mocked_plotly_figure_show):

        strategy = fixture["in_margin"]["strategy"]
        params = fixture["in_margin"]["params"]
        trading_costs = fixture["in_margin"]["trading_costs"]

        amount = 1000

        test_data = data.set_index("open_time")

        strategy_instance = strategy(**params, data=test_data)

        vect = VectorizedBacktester(
            strategy_instance,
            symbol="BTCUSDT",
            amount=amount,
            trading_costs=trading_costs,
            include_margin=True,
            leverage=leverage,
        )

        vect.run()

        print(vect.processed_data.to_dict(orient="records"))

        if len(vect.trades) > 0:
            assert (
                round(vect.trades[0].profit / vect.trades[0].pnl * leverage) == amount
            )

        for trade in vect.trades:
            assert trade.liquidation_price is not None

        for i, d in enumerate(vect.processed_data.to_dict(orient="records")):
            for key in d:
                assert d[key] == pytest.approx(
                    fixture["out_margin"]["expected_results"][leverage][i][key], 0.2
                )

    @pytest.mark.parametrize(
        "leverage,symbol,second_leverage,exception",
        [
            pytest.param(-1, "BTCUSDT", 1, LeverageInvalid, id="invalid_leverage"),
            pytest.param(1, "Invalid Symbol", 1, SymbolInvalid, id="invalid_symbol"),
            pytest.param(
                1, "BTCUSDT", -1, LeverageInvalid, id="invalid_leverage_on_run"
            ),
        ],
    )
    def test_exceptions(
        self, leverage, symbol, second_leverage, exception, mocked_plotly_figure_show
    ):

        strategy = MovingAverage(10)

        with pytest.raises(exception):

            vect = VectorizedBacktester(
                strategy, symbol=symbol, include_margin=True, leverage=leverage
            )

            vect.run(leverage=second_leverage)

    @pytest.mark.parametrize(
        "leverage",
        [pytest.param(1, id="leverage=1"), pytest.param(10, id="leverage=10")],
    )
    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_results_equal_to_iterative(
        self, leverage, fixture, mocked_plotly_figure_show
    ):
        strategy = fixture["in_margin"]["strategy"]
        params = fixture["in_margin"]["params"]
        trading_costs = fixture["in_margin"]["trading_costs"]

        test_data = data.set_index("open_time")

        strategy_instance = strategy(**params, data=test_data)

        vect = VectorizedBacktester(
            strategy_instance,
            symbol="BTCUSDT",
            trading_costs=trading_costs,
            include_margin=True,
            leverage=leverage,
        )

        ite = IterativeBacktester(
            strategy_instance,
            symbol="BTCUSDT",
            trading_costs=trading_costs,
            include_margin=True,
            leverage=leverage,
        )

        vect.run()
        ite.run()

        trades_vect = pd.DataFrame(vect.trades)
        trades_ite = pd.DataFrame(ite.trades)

        pd.testing.assert_series_equal(vect.results, ite.results)
        pd.testing.assert_series_equal(
            vect.processed_data[cum_returns], ite.processed_data[cum_returns]
        )
        pd.testing.assert_series_equal(
            vect.processed_data[cum_returns_tc], ite.processed_data[cum_returns_tc]
        )
        pd.testing.assert_series_equal(
            vect.processed_data[margin_ratio], ite.processed_data[margin_ratio]
        )
        pd.testing.assert_frame_equal(trades_vect, trades_ite)
