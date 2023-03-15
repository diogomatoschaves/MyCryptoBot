import os

import pandas as pd

from model.backtesting import IterativeBacktester, VectorizedBacktester
from model.tests.setup.fixtures.external_modules import mocked_matplotlib_show
from model.tests.setup.test_data.sample_data import data
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.test_setup import get_fixtures

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path)


cum_returns = "accumulated_strategy_returns"
cum_returns_tc = "accumulated_strategy_returns_tc"


class TestIterativeBacktester:
    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_run(self, fixture, mocked_matplotlib_show):

        strategy = fixture["in"]["strategy"]
        params = fixture["in"]["params"]
        trading_costs = fixture["in"]["trading_costs"]

        test_data = data.set_index("open_time")

        strategy_instance = strategy(**params, data=test_data)

        ite = IterativeBacktester(strategy_instance, trading_costs=trading_costs)

        ite.run()

        print(ite.processed_data.to_dict(orient="records"))

        for i, d in enumerate(ite.processed_data.to_dict(orient="records")):
            for key in d:
                assert d[key] == pytest.approx(
                    fixture["out"]["expected_results"][i][key], 0.2
                )

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_results_equal_to_vectorized(self, fixture, mocked_matplotlib_show):
        strategy = fixture["in"]["strategy"]
        params = fixture["in"]["params"]
        trading_costs = fixture["in"]["trading_costs"]

        test_data = data.set_index("open_time")

        strategy_instance = strategy(**params, data=test_data)

        ite = IterativeBacktester(strategy_instance, trading_costs=trading_costs)
        vect = VectorizedBacktester(strategy_instance, trading_costs=trading_costs)

        ite.run()
        vect.run()

        trades_ite = pd.DataFrame(ite.trades)
        trades_vect = pd.DataFrame(vect.trades)

        pd.testing.assert_series_equal(ite.results, vect.results)
        pd.testing.assert_series_equal(
            ite.processed_data[cum_returns], vect.processed_data[cum_returns]
        )
        pd.testing.assert_series_equal(
            ite.processed_data[cum_returns_tc], vect.processed_data[cum_returns_tc]
        )
        pd.testing.assert_frame_equal(trades_ite, trades_vect)
