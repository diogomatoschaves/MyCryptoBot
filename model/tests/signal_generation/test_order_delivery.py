from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
import pytz
from requests import ConnectionError as RequestsConnectionError

# initializing the service package first breaks the app <-> strategies
# import cycle (same entry order as the service tests)
import model.service  # noqa: F401  isort: skip
import model.signal_generation._signal_generation as signal_module
from model.signal_generation._exceptions import OrderDeliveryError, StaleSignal
from model.signal_generation._signal_generation import (
    compute_delivery_deadline,
    signal_failure_handler,
    trigger_order,
    MAX_DELIVERY_SECONDS,
)


@pytest.fixture
def mock_sleep(mocker):
    return mocker.patch.object(signal_module.time, "sleep")


@pytest.fixture
def mock_execute(mocker):
    return mocker.patch.object(signal_module, "execute_order")


def now_utc():
    return datetime.now(tz=pytz.utc)


class TestComputeDeliveryDeadline:

    def test_missing_enqueued_at_uses_job_budget(self):
        deadline = compute_delivery_deadline({"id": 1, "interval": "1h"})

        budget = (deadline - now_utc()).total_seconds()
        assert 0 < budget <= MAX_DELIVERY_SECONDS

    def test_fresh_signal_capped_by_job_budget(self):
        enqueued = now_utc().isoformat()

        deadline = compute_delivery_deadline(
            {"id": 1, "interval": "1h", "enqueued_at": enqueued}
        )

        budget = (deadline - now_utc()).total_seconds()
        assert budget <= MAX_DELIVERY_SECONDS

    def test_small_candle_capped_by_candle_close(self):
        enqueued = (now_utc() - timedelta(minutes=4, seconds=40)).isoformat()

        deadline = compute_delivery_deadline(
            {"id": 1, "interval": "5m", "enqueued_at": enqueued}
        )

        # only ~20s of the 5m candle remain - tighter than the 40s budget
        budget = (deadline - now_utc()).total_seconds()
        assert budget < MAX_DELIVERY_SECONDS

    def test_stale_signal_raises(self):
        enqueued = (now_utc() - timedelta(minutes=6)).isoformat()

        with pytest.raises(StaleSignal):
            compute_delivery_deadline(
                {"id": 1, "interval": "5m", "enqueued_at": enqueued}
            )

    def test_malformed_enqueued_at_falls_back(self):
        deadline = compute_delivery_deadline(
            {"id": 1, "interval": "1h", "enqueued_at": "not-a-date"}
        )

        assert deadline > now_utc()


class TestTriggerOrder:

    def test_success_returns_true(self, mock_execute, mock_sleep):
        mock_execute.return_value = {"success": True}

        assert trigger_order(1, 1, "token", deadline=now_utc() + timedelta(seconds=60)) is True
        mock_sleep.assert_not_called()

    def test_business_failure_returns_false_without_retry(self, mock_execute, mock_sleep):
        mock_execute.return_value = {
            "success": False, "code": "PIPELINE_NOT_ACTIVE", "message": "not active"
        }

        result = trigger_order(1, 1, "token", deadline=now_utc() + timedelta(seconds=600))

        assert result is False
        assert mock_execute.call_count == 1
        mock_sleep.assert_not_called()

    def test_transport_failure_retries_then_succeeds(self, mock_execute, mock_sleep):
        mock_execute.side_effect = [
            RequestsConnectionError("down"),
            {"success": False, "code": 502, "message": "bad gateway"},
            {"success": True},
        ]

        result = trigger_order(1, 1, "token", deadline=now_utc() + timedelta(seconds=600))

        assert result is True
        assert mock_execute.call_count == 3
        assert [call.args[0] for call in mock_sleep.call_args_list] == [5, 10]

    def test_exhausted_deadline_raises_order_delivery_error(self, mock_execute, mock_sleep):
        mock_execute.side_effect = RequestsConnectionError("down")

        with pytest.raises(OrderDeliveryError):
            trigger_order(1, 1, "token", deadline=now_utc() + timedelta(seconds=8))

        # one retry (5s backoff) fits inside 8s; the next (10s) does not
        # (sleep is mocked, so the clock barely advances between attempts)
        assert mock_execute.call_count == 2

    def test_no_deadline_fails_immediately_on_transport_error(self, mock_execute, mock_sleep):
        mock_execute.side_effect = RequestsConnectionError("down")

        with pytest.raises(OrderDeliveryError):
            trigger_order(1, 1, "token", deadline=None)

        assert mock_execute.call_count == 1
        mock_sleep.assert_not_called()


class TestSignalFailureHandler:

    def make_job(self, exc):
        job = MagicMock()
        job.args = ({"id": 7, "interval": "1h"}, "token", "")
        return job, type(exc), exc

    def test_order_delivery_error_is_critical(self, mocker):
        alert = mocker.patch.object(signal_module, "send_alert")
        job, exc_type, exc = self.make_job(OrderDeliveryError(7, 1))

        signal_failure_handler(job, None, exc_type, exc, None)

        alert.assert_called_once()
        assert alert.call_args.kwargs["severity"] == "critical"
        assert "7" in alert.call_args.kwargs["body"]

    def test_other_errors_are_warnings(self, mocker):
        alert = mocker.patch.object(signal_module, "send_alert")
        job, exc_type, exc = self.make_job(ValueError("boom"))

        signal_failure_handler(job, None, exc_type, exc, None)

        alert.assert_called_once()
        assert alert.call_args.kwargs["severity"] == "warning"
