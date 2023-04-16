import os

import pandas as pd

from model.backtesting import VectorizedBacktester, IterativeBacktester
from model.tests.setup.fixtures.external_modules import mocked_plotly_figure_show
from model.tests.setup.test_data.sample_data import data
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.test_setup import get_fixtures

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path)

cum_returns = "accumulated_strategy_returns"
cum_returns_tc = "accumulated_strategy_returns_tc"


class TestVectorizedBacktester:
    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_run(self, fixture, mocked_plotly_figure_show):

        strategy = fixture["in"]["strategy"]
        params = fixture["in"]["params"]
        trading_costs = fixture["in"]["trading_costs"]

        test_data = data.set_index("open_time")

        strategy_instance = strategy(**params, data=test_data)

        vect = VectorizedBacktester(strategy_instance, trading_costs=trading_costs)

        vect.run()

        print(vect.processed_data.to_dict(orient="records"))

        for i, d in enumerate(vect.processed_data.to_dict(orient="records")):
            for key in d:
                assert d[key] == pytest.approx(
                    fixture["out"]["expected_results"][i][key], 0.2
                ), print(d, key)

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_optimize_parameters(self, fixture, mocked_plotly_figure_show):

        strategy = fixture["in"]["strategy"]
        params = fixture["in"]["params"]
        optimization_params = fixture["in"]["optimization_params"]
        trading_costs = fixture["in"]["trading_costs"]

        test_data = data.set_index("open_time")

        strategy_instance = strategy(**params, data=test_data)

        vect = VectorizedBacktester(strategy_instance, trading_costs=trading_costs)

        optimization_results, perf = vect.optimize(optimization_params)

        print(optimization_results)

        assert (
            optimization_results == fixture["out"]["expected_optimization_results"][0]
        ).all()

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_results_equal_to_vectorized(self, fixture, mocked_plotly_figure_show):
        strategy = fixture["in"]["strategy"]
        params = fixture["in"]["params"]
        trading_costs = fixture["in"]["trading_costs"]

        test_data = data.set_index("open_time")

        strategy_instance = strategy(**params, data=test_data)

        vect = VectorizedBacktester(strategy_instance, trading_costs=trading_costs)
        ite = IterativeBacktester(strategy_instance, trading_costs=trading_costs)

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
        pd.testing.assert_frame_equal(trades_vect, trades_ite)
