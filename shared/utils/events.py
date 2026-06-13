"""
Pipeline lifecycle event publishing over redis pub/sub.

Any service can publish; the data service's /api/events SSE endpoint relays
the channel to connected dashboards so the UI reflects bot state changes
within a second instead of waiting for the next poll.

Like the notifier, this is a side channel: publishing must NEVER raise into
the calling code path, and it is a no-op under TEST.
"""

import json
import logging
import os
import threading
from datetime import datetime, timezone

import redis

from shared.utils.settings import settings

PIPELINE_EVENTS_CHANNEL = "pipeline-events"

EVENT_STARTED = "pipeline.started"
EVENT_STOPPED = "pipeline.stopped"
EVENT_DEACTIVATED = "pipeline.deactivated"
EVENT_START_FAILED = "pipeline.start_failed"

# lazy module-level connection: created on first publish, reset on failure so
# a dead connection is never sticky. redis-py clients are thread-safe; the
# lock only prevents concurrent first-publishes creating duplicate clients.
_connection = None
_connection_lock = threading.Lock()


def _reset_state():
    """Test hook: drop the cached connection."""
    global _connection
    _connection = None


def _get_connection():
    global _connection
    if _connection is None:
        with _connection_lock:
            if _connection is None:
                _connection = redis.from_url(settings.redis_url)
    return _connection


def publish_pipeline_event(event_type, pipeline_id, reason=None, **extra):
    """
    Publishes a pipeline lifecycle event. Returns True if the event was
    published, False otherwise (test mode or redis unavailable).

    Payload keys are camelCase to match the REST API responses the frontend
    already consumes.
    """
    global _connection

    try:
        if os.getenv("TEST"):
            return False

        payload = {
            "type": event_type,
            "pipelineId": pipeline_id,
            "reason": reason,
            "active": event_type == EVENT_STARTED,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        payload.update(extra)

        _get_connection().publish(PIPELINE_EVENTS_CHANNEL, json.dumps(payload))

        return True

    except Exception as e:
        logging.warning(f"Failed to publish pipeline event {event_type}: {e}")
        _connection = None
        return False
