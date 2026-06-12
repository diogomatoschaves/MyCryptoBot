import logging
import os
import time

import requests

SEVERITY_EMOJI = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}

DEFAULT_THROTTLE_SECONDS = 300
_MAX_CACHE_ENTRIES = 256

# fingerprint -> (monotonic timestamp, ttl) of the last send attempt
_last_sent = {}
_warned_unconfigured = False


def _reset_state():
    """Test hook: clear the throttle cache and the one-time warning flag."""
    global _warned_unconfigured
    _last_sent.clear()
    _warned_unconfigured = False


def _prune_cache(now):
    if len(_last_sent) <= _MAX_CACHE_ENTRIES:
        return
    expired = [key for key, (sent_at, ttl) in _last_sent.items() if now - sent_at >= ttl]
    for key in expired:
        _last_sent.pop(key, None)


def send_alert(title, body, severity="warning", dedup_key=None, throttle_seconds=DEFAULT_THROTTLE_SECONDS):
    """
    Sends an operational alert to Telegram. Returns True if a message was
    actually sent, False otherwise (test mode, unconfigured, throttled, or
    send failure).

    This is a side channel: it must NEVER raise into the calling code path,
    and it deliberately reads its configuration (TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID) from the environment at call time so tests can toggle
    it per-case.

    Duplicate suppression is in-process only: each service runs as a single
    long-lived process, and the spam vector is a flapping condition inside
    one process. The same incident observed by two services produces one
    message per service, which is informative rather than noise.
    """
    global _warned_unconfigured

    try:
        if os.getenv("TEST"):
            return False

        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            if not _warned_unconfigured:
                _warned_unconfigured = True
                logging.warning(
                    "Telegram alerts not configured (TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID unset)."
                )
            return False

        fingerprint = dedup_key if dedup_key else "{}:{}:{}".format(severity, title, body)

        now = time.monotonic()
        previous = _last_sent.get(fingerprint)
        if previous is not None and now - previous[0] < previous[1]:
            return False

        # recorded before the HTTP call so a failing Telegram API cannot
        # itself produce a burst of retries within the throttle window
        _last_sent[fingerprint] = (now, throttle_seconds)
        _prune_cache(now)

        emoji = SEVERITY_EMOJI.get(severity, SEVERITY_EMOJI["warning"])
        # plain text on purpose: parse_mode would make sends fail on
        # unescaped markdown characters in symbol names or error messages
        text = "{} {}\n\n{}".format(emoji, title, body)

        response = requests.post(
            "https://api.telegram.org/bot{}/sendMessage".format(token),
            json={"chat_id": chat_id, "text": text},
            timeout=(3, 5),
        )
        response.raise_for_status()

        return True

    except Exception as e:
        logging.warning("Failed to send Telegram alert: {}".format(e))
        return False
