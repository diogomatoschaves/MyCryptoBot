from model.signal_generation import signal_generator, trigger_order
from model.tests.setup.fixtures.internal_modules import (
    mock_execute_order,
    mock_trigger_order,
    mock_redis_connection,
    mock_settings_env_vars,
    mock_get_data,
    spy_upload_file,
    mock_local_models_storage,
    create_mock_file
)
from model.tests.setup.fixtures.external_modules import mock_boto3_client
from model.tests.setup.test_data.sample_data import data
from shared.utils.exceptions import StrategyInvalid
from shared.utils.tests.fixtures.models import *


class TestSignalGeneration:
    @pytest.mark.parametrize(
        "pipeline_id,side_effect,expected_value,upload_call_count",
        [
            pytest.param(
                1,
                data,
                True,
                1,
                id="ValidInput",
            ),
            pytest.param(
                2,
                [],
                False,
                0,
                id="EmptyDataFrame",
            ),
        ],
    )
    def test_signal_generator(
        self,
        pipeline_id,
        side_effect,
        expected_value,
        upload_call_count,
        mock_settings_env_vars,
        mock_redis_connection,
        mock_boto3_client,
        create_mock_file,
        mock_local_models_storage,
        spy_upload_file,
        create_pipeline,
        create_pipeline_2,
        create_pipeline_with_invalid_strategy,
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

        pipeline = Pipeline.objects.get(id=pipeline_id)

        pipeline_dict = dict(
            id=pipeline.id,
            strategies=[obj.as_json() for obj in pipeline.strategy.all()],
            strategy_combination=pipeline.strategy_combination,
            symbol=pipeline.symbol.name,
            exchange=pipeline.exchange.name,
            interval=pipeline.interval
        )

        params = {
            "pipeline": pipeline_dict,
            "bearer_token": "abc"
        }

        res = signal_generator(**params)

        assert res == expected_value

        assert spy_upload_file.call_count == upload_call_count

    @pytest.mark.parametrize(
        "pipeline_id,exception",
        [
            pytest.param(
                7,
                StrategyInvalid,
                id="raise-StrategyInvalid"
            )
        ],
    )
    def test_signal_generator_raise_exception(
        self,
        pipeline_id,
        exception,
        mock_settings_env_vars,
        mock_boto3_client,
        mock_redis_connection,
        create_pipeline_with_invalid_strategy,
        mock_get_data,
        mock_trigger_order,
    ):
        """
        GIVEN some params
        WHEN the method get_signal is called
        THEN the return value is equal to the expected response

        """
        mock_get_data.return_value = data

        pipeline = Pipeline.objects.get(id=pipeline_id)

        pipeline_dict = dict(
            id=pipeline.id,
            strategies=[obj.as_json() for obj in pipeline.strategy.all()],
            strategy_combination=pipeline.strategy_combination,
            symbol=pipeline.symbol.name,
            exchange=pipeline.exchange.name,
            interval=pipeline.interval
        )

        params = {
            "pipeline": pipeline_dict,
            "bearer_token": "abc"
        }

        with pytest.raises(exception) as excinfo:
            signal_generator(**params)

        assert excinfo.type == exception

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
    def test_trigger_order(
        self,
        side_effect,
        expected_value,
        mock_execute_order,
        mock_redis_connection,
        mock_boto3_client
    ):
        """
        GIVEN some params
        WHEN the method trigger_order is called
        THEN the return value is equal to the expected response

        """

        mock_execute_order.return_value = side_effect

        params = {"signal": 1, "pipeline_id": 1, "bearer_token": "abc"}

        res = trigger_order(**params)

        assert res == expected_value
