import os

from model.backtesting import VectorizedBacktester
from model.tests.setup.fixtures.external_modules import mocked_matplotlib_show
from model.tests.setup.test_data.sample_data import data
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.test_setup import get_fixtures

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path)


class TestVectorizedBacktester:
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

        strategy_instance = strategy(**params, data=data)

        vect = VectorizedBacktester(strategy_instance, trading_costs=trading_costs)

        vect.run()

        print(vect.results.to_dict(orient="records"))

        for i, d in enumerate(vect.results.to_dict(orient="records")):
            for key in d:
                assert d[key] == pytest.approx(fixture["out"]["expected_results"][i][key], 0.2)

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_optimize_parameters(self, fixture, mocked_matplotlib_show):

        strategy = fixture["in"]["strategy"]
        params = fixture["in"]["params"]
        optimization_params = fixture["in"]["optimization_params"]
        trading_costs = fixture["in"]["trading_costs"]

        strategy_instance = strategy(**params, data=data)

        vect = VectorizedBacktester(strategy_instance, trading_costs=trading_costs)

        optimization_results, perf = vect.optimize(optimization_params)

        print(optimization_results)

        assert (
            optimization_results == fixture["out"]["expected_optimization_results"][0]
        ).all()
