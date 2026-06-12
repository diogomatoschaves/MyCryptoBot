import logging

import pytest

from shared.utils import notifier
from shared.utils.notifier import send_alert


@pytest.fixture(autouse=True)
def reset_notifier_state():
    notifier._reset_state()
    yield
    notifier._reset_state()


@pytest.fixture
def configured(monkeypatch):
    """Telegram configured and TEST mode disabled, as in a real deployment."""
    monkeypatch.delenv("TEST", raising=False)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")


@pytest.fixture
def mock_post(mocker):
    return mocker.patch("shared.utils.notifier.requests.post")


class TestSendAlert:

    def test_noop_when_test_env_set(self, monkeypatch, mock_post):
        # pytest.ini sets TEST=true; tokens being present must not matter
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")

        assert send_alert("title", "body") is False
        mock_post.assert_not_called()

    def test_noop_and_single_warning_when_unconfigured(self, monkeypatch, mock_post, caplog):
        monkeypatch.delenv("TEST", raising=False)
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        with caplog.at_level(logging.WARNING):
            assert send_alert("title", "body") is False
            assert send_alert("other", "body") is False

        mock_post.assert_not_called()
        warnings = [r for r in caplog.records if "not configured" in r.message]
        assert len(warnings) == 1

    def test_sends_message(self, configured, mock_post):
        result = send_alert("Pipeline stopped", "details here", severity="critical")

        assert result is True
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "test-token" in args[0]
        assert kwargs["json"]["chat_id"] == "12345"
        assert kwargs["json"]["text"].startswith("🚨 Pipeline stopped")
        assert "details here" in kwargs["json"]["text"]
        assert kwargs["timeout"] == (3, 5)

    def test_unknown_severity_falls_back_to_warning(self, configured, mock_post):
        assert send_alert("title", "body", severity="bogus") is True
        text = mock_post.call_args[1]["json"]["text"]
        assert text.startswith("⚠️")

    def test_never_raises(self, configured, mock_post):
        mock_post.side_effect = Exception("boom")

        assert send_alert("title", "body") is False

    def test_throttles_duplicate_fingerprints(self, configured, mock_post):
        assert send_alert("title", "body") is True
        assert send_alert("title", "body") is False
        assert mock_post.call_count == 1

        # a distinct dedup_key is a distinct fingerprint
        assert send_alert("title", "body", dedup_key="other") is True
        assert mock_post.call_count == 2

    def test_sends_again_after_ttl_expires(self, configured, mock_post, mocker):
        clock = mocker.patch("shared.utils.notifier.time.monotonic")

        clock.return_value = 1000.0
        assert send_alert("title", "body", throttle_seconds=300) is True

        clock.return_value = 1100.0
        assert send_alert("title", "body", throttle_seconds=300) is False

        clock.return_value = 1301.0
        assert send_alert("title", "body", throttle_seconds=300) is True

        assert mock_post.call_count == 2

    def test_failed_send_is_throttled_too(self, configured, mock_post):
        # the throttle entry is recorded before the HTTP call on purpose
        mock_post.side_effect = Exception("boom")
        assert send_alert("title", "body") is False

        mock_post.side_effect = None
        assert send_alert("title", "body") is False
        assert mock_post.call_count == 1
