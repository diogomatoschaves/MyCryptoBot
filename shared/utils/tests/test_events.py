import json

import pytest

from shared.utils import events
from shared.utils.events import (
    publish_pipeline_event,
    PIPELINE_EVENTS_CHANNEL,
    EVENT_STARTED,
    EVENT_START_FAILED,
)


@pytest.fixture(autouse=True)
def reset_events_state():
    events._reset_state()
    yield
    events._reset_state()


@pytest.fixture
def live_mode(monkeypatch):
    monkeypatch.delenv("TEST", raising=False)


@pytest.fixture
def mock_redis(mocker):
    return mocker.patch("shared.utils.events.redis.from_url")


class TestPublishPipelineEvent:

    def test_noop_when_test_env_set(self, mock_redis):
        # pytest.ini sets TEST=true
        assert publish_pipeline_event(EVENT_STARTED, 1) is False
        mock_redis.assert_not_called()

    def test_publishes_payload(self, live_mode, mock_redis):
        result = publish_pipeline_event(
            EVENT_START_FAILED, 12, reason="websocket failed", restarted=True
        )

        assert result is True
        channel, raw = mock_redis.return_value.publish.call_args.args
        assert channel == PIPELINE_EVENTS_CHANNEL

        payload = json.loads(raw)
        assert payload["type"] == EVENT_START_FAILED
        assert payload["pipelineId"] == 12
        assert payload["reason"] == "websocket failed"
        assert payload["active"] is False
        assert payload["restarted"] is True
        assert "timestamp" in payload

    def test_active_true_only_for_started(self, live_mode, mock_redis):
        publish_pipeline_event(EVENT_STARTED, 1)

        payload = json.loads(mock_redis.return_value.publish.call_args.args[1])
        assert payload["active"] is True

    def test_never_raises_and_resets_connection(self, live_mode, mock_redis):
        mock_redis.return_value.publish.side_effect = ConnectionError("redis down")

        assert publish_pipeline_event(EVENT_STARTED, 1) is False
        assert events._connection is None

        # next publish reconnects
        mock_redis.return_value.publish.side_effect = None
        assert publish_pipeline_event(EVENT_STARTED, 1) is True

    def test_connection_is_lazy_and_cached(self, live_mode, mock_redis):
        publish_pipeline_event(EVENT_STARTED, 1)
        publish_pipeline_event(EVENT_STARTED, 2)

        assert mock_redis.call_count == 1
