"""
Server-Sent Events endpoint relaying pipeline lifecycle events to the
dashboard. Services publish on the redis channel (shared/utils/events.py);
each connected client gets its own pubsub subscription - this is a
single-user dashboard, so a handful of subscriptions at most.
"""

import time

import redis
from flask import Blueprint, Response
from flask_jwt_extended import jwt_required

from shared.utils.decorators import general_app_error
from shared.utils.events import PIPELINE_EVENTS_CHANNEL
from shared.utils.settings import settings

events_bp = Blueprint('events', __name__)

# below Heroku's 55s router idle timeout and nginx's 60s proxy_read_timeout
KEEPALIVE_SECONDS = 15


def event_stream(pubsub, keepalive=KEEPALIVE_SECONDS, connection=None):
    """
    Yields SSE frames from a redis pubsub subscription.

    Uses get_message(timeout=...) rather than listen(): listen() blocks
    indefinitely, which would prevent both keepalive comments and client
    disconnect detection (a disconnect only surfaces as a failed write on
    the next yield).
    """
    try:
        # comment frame: flushes response headers immediately
        yield ': connected\n\n'

        last_beat = time.monotonic()

        while True:
            message = pubsub.get_message(timeout=keepalive)

            if message is not None and message.get('type') == 'message':
                data = message['data']
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                yield 'data: ' + data + '\n\n'

            now = time.monotonic()
            if now - last_beat >= keepalive:
                # SSE comment, ignored by the browser
                yield ': keepalive\n\n'
                last_beat = now
    finally:
        # pubsub.close() releases the subscription socket but not the parent
        # client/pool - close both so reconnect loops can't accumulate sockets
        try:
            pubsub.close()
        except Exception:
            pass
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


@events_bp.get('/events')
@general_app_error
@jwt_required()
def pipeline_events():
    # subscribe BEFORE building the streaming response: a redis outage then
    # fails fast with a normal error response instead of a half-open stream
    connection = redis.from_url(settings.redis_url)
    pubsub = connection.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(PIPELINE_EVENTS_CHANNEL)

    response = Response(
        event_stream(pubsub, connection=connection), mimetype='text/event-stream'
    )
    response.headers['Cache-Control'] = 'no-cache'
    # disables nginx per-response buffering so frames reach the browser live
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    return response
