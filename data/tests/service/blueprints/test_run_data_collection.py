import pytest

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", "true")
    import data.service.blueprints.bots_api._helpers as helpers_module
    from data.service.blueprints.bots_api._helpers import _run_data_collection

from database.model.models import Pipeline
from shared.utils.tests.fixtures.models import (  # noqa: F401
    create_exchange, create_symbol, create_assets, create_pipeline,
)


@pytest.fixture
def module_mocks(mocker):
    return {
        "initialize": mocker.patch.object(helpers_module, "initialize_data_collection"),
        "stop_instance": mocker.patch.object(helpers_module, "stop_instance"),
        "execution_stop": mocker.patch.object(helpers_module, "start_stop_symbol_trading"),
        "alert": mocker.patch.object(helpers_module, "send_alert"),
        "event": mocker.patch.object(helpers_module, "publish_pipeline_event"),
    }


@pytest.mark.django_db
class TestRunDataCollection:
    """An exception in the executor task used to be silently swallowed,
    leaving a zombie pipeline marked active with no data flowing."""

    def test_failure_deactivates_cleans_up_and_publishes(
        self, module_mocks, create_pipeline
    ):
        module_mocks["initialize"].side_effect = RuntimeError("websocket died")

        _run_data_collection(create_pipeline, "")

        pipeline = Pipeline.objects.get(id=1)
        assert pipeline.active is False
        assert pipeline.open_time is None

        module_mocks["stop_instance"].assert_called_once()
        module_mocks["execution_stop"].assert_called_once()
        assert module_mocks["execution_stop"].call_args.args[0]["force"] is True

        assert module_mocks["alert"].call_args.kwargs["severity"] == "critical"
        event_call = module_mocks["event"].call_args
        assert event_call.args[0] == "pipeline.start_failed"
        assert "websocket died" in event_call.kwargs["reason"]

    def test_cleanup_failures_do_not_mask_deactivation(
        self, module_mocks, create_pipeline
    ):
        module_mocks["initialize"].side_effect = RuntimeError("boom")
        module_mocks["stop_instance"].side_effect = Exception("cleanup failed")
        module_mocks["execution_stop"].side_effect = Exception("execution down")

        _run_data_collection(create_pipeline, "")

        assert Pipeline.objects.get(id=1).active is False
        module_mocks["alert"].assert_called_once()

    def test_success_has_no_side_effects(self, module_mocks, create_pipeline):
        _run_data_collection(create_pipeline, "")

        assert Pipeline.objects.get(id=1).active is True
        module_mocks["stop_instance"].assert_not_called()
        module_mocks["alert"].assert_not_called()
        module_mocks["event"].assert_not_called()


@pytest.fixture
def start_mocks(mocker):
    return {
        "loading": mocker.patch.object(helpers_module, "add_pipeline_loading"),
        "header": mocker.patch.object(helpers_module, "get_logging_row_header", return_value=""),
        "execution": mocker.patch.object(helpers_module, "start_stop_symbol_trading"),
        "event": mocker.patch.object(helpers_module, "publish_pipeline_event"),
        "submit": mocker.patch.object(helpers_module.executor, "submit"),
    }


@pytest.mark.django_db
class TestStartSymbolTradingResponseGuard:

    def test_null_execution_response_fails_gracefully(self, start_mocks, create_pipeline):
        # the execution service returning null (e.g. an endpoint path with no
        # explicit return) used to crash on response["success"]
        start_mocks["execution"].return_value = None

        from data.service.blueprints.bots_api._helpers import start_symbol_trading
        response = start_symbol_trading(create_pipeline)

        assert response["success"] is False
        assert response["code"] == "NO_RESPONSE"
        assert Pipeline.objects.get(id=1).active is False
        start_mocks["submit"].assert_not_called()
        assert start_mocks["event"].call_args.args[0] == "pipeline.start_failed"

    def test_response_without_code_key_fails_gracefully(self, start_mocks, create_pipeline):
        start_mocks["execution"].return_value = {"success": False, "message": "boom"}

        from data.service.blueprints.bots_api._helpers import start_symbol_trading
        response = start_symbol_trading(create_pipeline)

        assert response["success"] is False
        assert Pipeline.objects.get(id=1).active is False
