from model.backtesting import VectorizedBacktester
from model.strategies import MovingAverage, Momentum, BollingerBands
from model.tests.setup.fixtures.external_modules import mocked_plotly_figure_show
from model.tests.setup.test_data.sample_data import data
from shared.utils.exceptions import StrategyRequired, StrategyInvalid
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.test_setup import get_fixtures
from model.backtesting.combining import StrategyCombiner

current_path = os.path.dirname(os.path.realpath(__file__))
fixtures = get_fixtures(current_path)


class TestStrategyCombiner:

    @pytest.mark.parametrize(
        "input_params,exception",
        [
            pytest.param(
                {
                    "strategies": []
                },
                StrategyRequired,
                id='empty-strategies'
            ),
            pytest.param(
                {
                    "strategies": [VectorizedBacktester, MovingAverage(2)]
                },
                StrategyInvalid,
                id='invalid-strategy'
            ),
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Union"
                },
                Exception,
                id='invalid-method'
            )
        ],
    )
    def test_strategy_combiner_input_validation(
        self,
        input_params,
        exception
    ):
        test_data = data.set_index("open_time")

        # Initialize StrategyCombiner with the provided instances, method, and data
        with pytest.raises(exception) as excinfo:
            StrategyCombiner(**input_params, data=test_data)

            assert excinfo.type == exception

    @pytest.mark.parametrize(
        "input_params,expected_results",
        [
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Majority"
                },
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, -1.0, 0.0, -1.0, 0.0],
                id='2_strategies-Majority'
            ),
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2)],
                    "method": "Unanimous"
                },
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, -1.0, 0.0, -1.0, 0.0],
                id='2_strategies-Unanimous'
            ),
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2), BollingerBands(3, 1)],
                    "method": "Majority"
                },
                [0.0, 0.0, 0.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0],
                id='3_strategies-Majority'
            ),
            pytest.param(
                {
                    "strategies": [Momentum(2), MovingAverage(2), BollingerBands(3, 1)],
                    "method": "Unanimous"
                },
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                id='3_strategies-Unanimous'
            )
        ],
    )
    def test_strategy_combiner(
        self,
        input_params,
        expected_results
    ):
        test_data = data.set_index("open_time")

        combiner = StrategyCombiner(**input_params, data=test_data)

        combiner.calculate_positions(combiner.data)

        print(combiner.data.to_dict(orient="records"))

        assert combiner.data["side"].to_list() == expected_results

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_strategy_combiner_with_backtester(
        self, fixture, mocked_plotly_figure_show
    ):
        # Extract strategy instances and parameters from the fixture
        strategies = fixture["in"]["strategies"]
        method = fixture["in"]["method"]
        backtesting_class = fixture["in"]["backtester"]

        test_data = data.set_index("open_time")

        # Initialize StrategyCombiner with the provided instances, method, and data
        strategy_combiner = StrategyCombiner(strategies, method, data=test_data)

        backtester = backtesting_class(strategy_combiner, trading_costs=0.1)

        # Run the backtester
        backtester.run()

        print(backtester.processed_data.to_dict(orient="records"))

        position_cols = [
            col for col in backtester.processed_data.columns if "side" in col
        ]

        assert len(strategies) == len(position_cols) - 1

        for i, d in enumerate(backtester.processed_data.to_dict(orient="records")):
            for key in d:
                assert d[key] == pytest.approx(
                    fixture["out"]["expected_results"][i][key], 0.2
                )
