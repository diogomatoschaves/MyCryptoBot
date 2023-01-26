from model.service.helpers.signal_generator import send_signal, trigger_order
from model.tests.setup.fixtures.internal_modules import *
from model.tests.setup.test_data.sample_data import sample_structured_data
from model.strategies.properties import STRATEGIES
from shared.utils.tests.fixtures.models import *


def inject_fixture(strategy):
    globals()[strategy] = mock_strategy_factory(strategy)


for strategy in STRATEGIES:
    inject_fixture(strategy)


class TestSignalGeneration:
    @pytest.mark.parametrize(
        "strategy,side_effect,expected_value",
        [
            pytest.param(
                "MovingAverageConvergenceDivergence",
                sample_structured_data,
                True,
                id="MovingAverageConvergenceDivergence",
            ),
            pytest.param(
                "MovingAverage",
                sample_structured_data,
                True,
                id="MovingAverage",
            ),
            pytest.param(
                "MovingAverageCrossover",
                sample_structured_data,
                True,
                id="MovingAverageCrossover",
            ),
            pytest.param(
                "BollingerBands",
                sample_structured_data,
                True,
                id="BollingerBands",
            ),
            pytest.param(
                "Momentum",
                sample_structured_data,
                True,
                id="Momentum",
            ),
            pytest.param(
                "InvalidStrategy",
                sample_structured_data,
                False,
                id="InvalidStrategy",
            ),
            pytest.param(
                "EmptyDataFrame",
                [],
                False,
                id="EmptyDataFrame",
            ),
        ],
    )
    def test_send_signal(
        self,
        strategy,
        side_effect,
        expected_value,
        mock_settings_env_vars,
        mock_redis_connection,
        MovingAverageConvergenceDivergence,
        MovingAverage,
        MovingAverageCrossover,
        BollingerBands,
        Momentum,
        mock_get_data,
        mock_trigger_order,
    ):
        """
        GIVEN some params
        WHEN the method get_signal is called
        THEN the return value is equal to the expected response

        """

        mock_get_data.return_value = side_effect
        mock_trigger_order.return_value = True

        params = {
            "pipeline_id": 1,
            "symbol": "BTC",
            "strategy": strategy,
            "candle_size": "1h",
            "exchange": "Binance",
            "bearer_token": "abc"
        }

        res = send_signal(**params)

        assert res == expected_value

    @pytest.mark.parametrize(
        "side_effect,expected_value",
        [
            pytest.param(
                {"success": True, "message": "Success"},
                True,
                id="EXECUTE_ORDER_SUCCESS",
            ),
            pytest.param(
                {"success": False, "message": "Fail"},
                False,
                id="EXECUTE_ORDER_FAIL",
            ),
        ],
    )
    def test_trigger_order(self, side_effect, expected_value, mock_execute_order, mock_redis_connection):
        """
        GIVEN some params
        WHEN the method trigger_order is called
        THEN the return value is equal to the expected response

        """

        mock_execute_order.return_value = side_effect

        params = {"signal": 1, "pipeline_id": 1, "bearer_token": "abc"}

        res = trigger_order(**params)

        assert res == expected_value
