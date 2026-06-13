import pytest

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", "true")
    import data.service.blueprints.events as events_blueprint
    from data.service.blueprints.events import event_stream

from data.tests.setup.fixtures.app import *  # noqa: F401,F403
from data.tests.setup.fixtures.internal_modules import *  # noqa: F401,F403
from data.tests.setup.fixtures.external_modules import *  # noqa: F401,F403
from shared.utils.tests.fixtures.models import *  # noqa: F401,F403
from shared.utils.tests.fixtures.external_modules import mock_jwt_required  # noqa: F401


class FakePubSub:

    def __init__(self, messages=None):
        self.messages = list(messages or [])
        self.closed = False

    def subscribe(self, channel):
        self.subscribed = channel

    def get_message(self, timeout=None):
        if self.messages:
            return self.messages.pop(0)
        return None

    def close(self):
        self.closed = True


class TestEventStream:

    def test_yields_connected_then_data_then_keepalive(self):
        pubsub = FakePubSub([
            {"type": "message", "data": b'{"type": "pipeline.stopped", "pipelineId": 1}'},
        ])
        stream = event_stream(pubsub, keepalive=0)

        assert next(stream) == ': connected\n\n'
        assert next(stream) == 'data: {"type": "pipeline.stopped", "pipelineId": 1}\n\n'
        # queue drained: the next frame is a keepalive comment
        assert next(stream) == ': keepalive\n\n'

        stream.close()
        assert pubsub.closed is True

    def test_ignores_non_message_frames(self):
        pubsub = FakePubSub([
            {"type": "subscribe", "data": 1},
            {"type": "message", "data": '{"type": "pipeline.started"}'},
        ])
        stream = event_stream(pubsub, keepalive=0)

        next(stream)  # connected
        # subscribe frame skipped; with keepalive=0 a beat may interleave
        frames = [next(stream), next(stream)]
        assert any(frame == 'data: {"type": "pipeline.started"}\n\n' for frame in frames)

        stream.close()

    def test_pubsub_closed_even_when_close_raises(self):
        class ExplodingPubSub(FakePubSub):
            def close(self):
                super().close()
                raise RuntimeError("already closed")

        pubsub = ExplodingPubSub()
        stream = event_stream(pubsub, keepalive=0)
        next(stream)

        # GeneratorExit -> finally -> close() raising must not propagate
        stream.close()
        assert pubsub.closed is True


class TestEventsEndpoint:

    def test_streams_with_sse_headers(self, client, mocker):
        fake_pubsub = FakePubSub()
        fake_redis = mocker.MagicMock()
        fake_redis.pubsub.return_value = fake_pubsub
        mocker.patch.object(events_blueprint.redis, "from_url", return_value=fake_redis)

        response = client.get('/api/events', buffered=False)

        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
        assert response.headers['Cache-Control'] == 'no-cache'
        assert response.headers['X-Accel-Buffering'] == 'no'

        # read exactly one frame, then close - never iterate an infinite stream
        first_chunk = next(response.response)
        if isinstance(first_chunk, bytes):
            first_chunk = first_chunk.decode()
        assert 'connected' in first_chunk

        response.response.close()
        assert fake_pubsub.closed is True

    def test_redis_outage_fails_fast(self, client, mocker):
        mocker.patch.object(
            events_blueprint.redis, "from_url",
            side_effect=ConnectionError("redis down"),
        )

        response = client.get('/api/events')

        assert response.status_code == 500
