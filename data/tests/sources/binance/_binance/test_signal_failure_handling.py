from unittest.mock import MagicMock

import pytest

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    import data.sources.binance._binance as binance_module
    from data.sources.binance import BinanceDataHandler


class HandlerStub:
    """generate_new_signal exercised without constructing the full
    websocket-backed handler."""

    pipeline_id = 1
    symbol = "BTCUSDT"
    MAX_CONSECUTIVE_FAILURES = BinanceDataHandler.MAX_CONSECUTIVE_FAILURES
    generate_new_signal = BinanceDataHandler.generate_new_signal


@pytest.fixture
def module_mocks(mocker):
    return {
        "cache": mocker.patch.object(binance_module, "cache"),
        "stop_pipeline": mocker.patch.object(binance_module, "stop_pipeline"),
        "send_alert": mocker.patch.object(binance_module, "send_alert"),
    }


class TestGenerateNewSignalFailureHandling:

    def test_too_many_retries_does_not_reenqueue(self, mocker, module_mocks):
        # regression: this used to recurse into a fresh trigger_signal,
        # enqueueing a duplicate job while the first might still be running
        trigger = mocker.patch.object(
            binance_module, "trigger_signal",
            return_value=(False, "Too many retries"),
        )
        module_mocks["cache"].incr.return_value = 1

        result = HandlerStub().generate_new_signal("")

        assert result is False
        assert trigger.call_count == 1
        module_mocks["cache"].incr.assert_called_once()
        module_mocks["stop_pipeline"].assert_not_called()
        assert module_mocks["send_alert"].call_args.kwargs["severity"] == "warning"

    def test_threshold_stops_pipeline_with_critical_alert(self, mocker, module_mocks):
        mocker.patch.object(
            binance_module, "trigger_signal",
            return_value=(False, "some failure"),
        )
        module_mocks["cache"].incr.return_value = HandlerStub.MAX_CONSECUTIVE_FAILURES

        result = HandlerStub().generate_new_signal("")

        assert result is False
        module_mocks["stop_pipeline"].assert_called_once()
        assert module_mocks["send_alert"].call_args.kwargs["severity"] == "critical"

    def test_success_clears_failure_counter(self, mocker, module_mocks):
        mocker.patch.object(
            binance_module, "trigger_signal", return_value=(True, "ok"),
        )

        result = HandlerStub().generate_new_signal("")

        assert result is True
        module_mocks["cache"].delete.assert_called_once()
        module_mocks["send_alert"].assert_not_called()
