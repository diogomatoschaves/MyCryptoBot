import os

import pandas as pd

from model.backtesting import IterativeBacktester, VectorizedBacktester
from model.backtesting.combining import StrategyCombiner
from model.strategies import Momentum, MovingAverage, BollingerBands, MovingAverageCrossover
from model.tests.setup.fixtures.external_modules import mocked_plotly_figure_show
from model.tests.setup.test_data.sample_data import data
from shared.utils.exceptions import OptimizationParametersInvalid
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
    def test_run(self, fixture, mocked_plotly_figure_show):

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
    def test_results_equal_to_vectorized(self, fixture, mocked_plotly_figure_show):
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

    @pytest.mark.parametrize(
        "strategy,optimization_params,exception",
        [
            pytest.param(
                Momentum(2),
                [dict(window=(2, 4))],
                OptimizationParametersInvalid,
                id='wrong-optimization-parameters-single-strategy'
            ),
            pytest.param(
                StrategyCombiner([Momentum(2), MovingAverage(2)]),
                dict(window=(2, 4)),
                OptimizationParametersInvalid,
                id='wrong-optimization-parameters-multiple-strategy'
            ),
            pytest.param(
                StrategyCombiner([Momentum(2)]),
                [dict(window=(2, 4)), dict(ma=(2, 4))],
                OptimizationParametersInvalid,
                id='too-many-optimization-parameters-multiple-strategy'
            ),
            pytest.param(
                StrategyCombiner([Momentum(2), MovingAverage(2)]),
                [dict(window=(2, 4))],
                OptimizationParametersInvalid,
                id='too-few-optimization-parameters-multiple-strategy'
            ),
        ],
    )
    def test_optimize_parameters_input_validation(
        self,
        strategy,
        optimization_params,
        exception
    ):
        test_data = data.set_index("open_time")

        with pytest.raises(exception) as excinfo:
            backtester = IterativeBacktester(strategy)
            backtester.load_data(data=test_data)
            backtester.optimize(optimization_params)

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

        ite = IterativeBacktester(strategy_instance, trading_costs=trading_costs)

        optimization_results, perf = ite.optimize(optimization_params)

        assert optimization_results == fixture["out"]["expected_optimization_results"][0]

    @pytest.mark.parametrize(
        "input_params,optimization_params,expected_results",
        [
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Unanimous"
                },
                [{"window": (2, 4, 1)}, {"ma": (1, 3, 1)}],
                [{'window': 3.0}, {'ma': 2.0}],
                id='2_strategies-unanimous'
            ),
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Majority"
                },
                [{"window": (2, 4, 1)}, {"ma": (1, 3, 1)}],
                [{'window': 3.0}, {'ma': 1.0}],
                id='2_strategies-majority'
            ),
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2), BollingerBands(3, 1)],
                    "method": "Majority"
                },
                [{"window": (2, 4, 1)}, {"ma": (1, 3, 1)}, {}],
                [{'window': 3.0}, {'ma': 1.0}, {'ma': 3.0, 'sd': 1.0}],
                id='3_strategies-majority'
            ),
            pytest.param(
                {
                    "strategies": [MovingAverageCrossover(2, 5)],
                    "method": "Unanimous"
                },
                [{"sma_s": (2, 4, 1), "sma_l": (4, 6, 1)}],
                [{'sma_s': 3.0, 'sma_l': 4.0}],
                id='1_strategies-unanimous'
            ),
        ],
    )
    def test_optimize_parameters_combined_strategies(
        self,
        input_params,
        optimization_params,
        expected_results,
        mocked_plotly_figure_show
    ):
        test_data = data.set_index("open_time")

        strategy_instance = StrategyCombiner(**input_params, data=test_data)

        ite = IterativeBacktester(strategy_instance)

        optimization_results, perf = ite.optimize(optimization_params)

        assert optimization_results == expected_results

    @pytest.mark.parametrize(
        "input_params,optimization_params",
        [
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Unanimous"
                },
                [{"window": (2, 4, 1)}, {"ma": (1, 3, 1)}],
                id='2_strategies-unanimous'
            ),
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Majority"
                },
                [{"window": (2, 4, 1)}, {"ma": (1, 3, 1)}],
                id='2_strategies-majority'
            ),
        ],
    )
    def test_load_data_optimize_parameters_combined_strategies(
        self,
        input_params,
        optimization_params,
        mocked_plotly_figure_show
    ):
        test_data = data.set_index("open_time")

        strategy_instance_1 = StrategyCombiner(**input_params, data=test_data)
        strategy_instance_2 = StrategyCombiner(**input_params)

        ite_1 = IterativeBacktester(strategy_instance_1)
        ite_2 = IterativeBacktester(strategy_instance_2)
        ite_2.load_data(data=test_data)

        optimization_results_1, perf_1 = ite_1.optimize(optimization_params)
        optimization_results_2, perf_2 = ite_2.optimize(optimization_params)

        assert optimization_results_1 == optimization_results_2
        assert perf_1 == perf_2

    @pytest.mark.parametrize(
        "input_params,optimization_params",
        [
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Unanimous"
                },
                [{"window": (2, 4, 1)}, {"ma": (1, 3, 1)}],
                id='2_strategies-unanimous'
            ),
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Majority"
                },
                [{"window": (2, 4, 1)}, {"ma": (1, 3, 1)}],
                id='2_strategies-majority'
            ),
        ],
    )
    def test_optimize_parameters_combined_strategies_equal_to_vectorized(
        self,
        input_params,
        optimization_params,
        mocked_plotly_figure_show
    ):
        test_data = data.set_index("open_time")

        strategy_instance_1 = StrategyCombiner(**input_params, data=test_data)
        strategy_instance_2 = StrategyCombiner(**input_params, data=test_data)

        ite = IterativeBacktester(strategy_instance_1)
        vect = IterativeBacktester(strategy_instance_2)

        optimization_results_1, perf_1 = ite.optimize(optimization_params)
        optimization_results_2, perf_2 = vect.optimize(optimization_params)

        assert optimization_results_1 == optimization_results_2
        assert perf_1 == perf_2

