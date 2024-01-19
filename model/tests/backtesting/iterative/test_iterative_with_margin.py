import os

import pytest

from model.backtesting import IterativeBacktester
from model.strategies import MovingAverage
from model.tests.setup.fixtures.external_modules import mocked_plotly_figure_show
from model.tests.setup.test_data.sample_data import data
from shared.utils.exceptions import SymbolInvalid
from shared.utils.exceptions.leverage_invalid import LeverageInvalid
from shared.utils.tests.test_setup import get_fixtures

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path, keys=["in_margin", "out_margin"])


class TestIterativeBacktesterMargin:

    @pytest.mark.parametrize(
        "leverage",
        [
            pytest.param(
                1,
                id='leverage=1'
            ),
            pytest.param(
                10,
                id='leverage=10'
            )
        ],
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

        ite = IterativeBacktester(
            strategy_instance,
            symbol='BTCUSDT',
            amount=amount,
            trading_costs=trading_costs,
            include_margin=True,
            leverage=leverage
        )

        ite.run()

        print(ite.processed_data.to_dict(orient="records"))

        assert round(ite.trades[0].profit / ite.trades[0].pnl * leverage) == amount

        for trade in ite.trades:
            assert trade.liquidation_price is not None

        for i, d in enumerate(ite.processed_data.to_dict(orient="records")):
            for key in d:
                assert d[key] == pytest.approx(
                    fixture["out_margin"]["expected_results"][leverage][i][key], 0.2
                )

    @pytest.mark.parametrize(
        "leverage,symbol,second_leverage,exception",
        [
            pytest.param(
                -1,
                'BTCUSDT',
                1,
                LeverageInvalid,
                id='invalid_leverage'
            ),
            pytest.param(
                1,
                'Invalid Symbol',
                1,
                SymbolInvalid,
                id='invalid_symbol'
            ),
            pytest.param(
                1,
                'BTCUSDT',
                -1,
                LeverageInvalid,
                id='invalid_leverage_on_run'
            )
        ],
    )
    def test_exceptions(self, leverage, symbol, second_leverage, exception, mocked_plotly_figure_show):

        strategy = MovingAverage(10)

        with pytest.raises(exception):

            ite = IterativeBacktester(
                strategy,
                symbol=symbol,
                include_margin=True,
                leverage=leverage
            )

            ite.run(leverage=second_leverage)

    @pytest.mark.parametrize(
        "include_margin",
        [
            pytest.param(True, id="include_margin=True"),
            pytest.param(False, id="include_margin=False")
        ],
    )
    @pytest.mark.parametrize(
        "margin_threshold, expected_result",
        [
            pytest.param(0.1, 18, id="margin_threshold=0.1"),
            pytest.param(0.5, 45, id="margin_threshold=0.5"),
            pytest.param(1, 55, id="margin_threshold=1")
        ],
    )
    def test_maximum_leverage(
        self, include_margin, margin_threshold, expected_result, mocked_plotly_figure_show
    ):
        test_data = data.set_index("open_time")

        strategy_instance = MovingAverage(4, data=test_data)

        ite = IterativeBacktester(
            strategy_instance,
            symbol="BTCUSDT",
            include_margin=include_margin,
        )

        result = ite.maximum_leverage(margin_threshold=margin_threshold)

        assert result == expected_result
