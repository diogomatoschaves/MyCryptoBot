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

# (token, chat_id, fetched_at) cached briefly so alert bursts don't hit the DB
_credentials_cache = None
_CREDENTIALS_CACHE_TTL = 60

TELEGRAM_TOKEN_KEY = "telegram_bot_token"
TELEGRAM_CHAT_ID_KEY = "telegram_chat_id"


def _reset_state():
    """Test hook: clear the throttle cache, credential cache and the
    one-time warning flag."""
    global _warned_unconfigured, _credentials_cache
    _last_sent.clear()
    _warned_unconfigured = False
    _credentials_cache = None


def _read_db_credentials():
    """Reads the Telegram credentials saved from the dashboard. Imported
    lazily and guarded so the notifier stays usable (as a no-op) in any
    context where the database is unavailable."""
    try:
        from database.model.models import AppSetting

        rows = dict(
            AppSetting.objects.filter(
                key__in=[TELEGRAM_TOKEN_KEY, TELEGRAM_CHAT_ID_KEY]
            ).values_list("key", "value")
        )
        return rows.get(TELEGRAM_TOKEN_KEY) or None, rows.get(TELEGRAM_CHAT_ID_KEY) or None
    except Exception as e:
        logging.debug("Could not read Telegram settings from the database: {}".format(e))
        return None, None


def get_telegram_credentials():
    """Resolves the bot token and chat id: environment variables win, the
    database settings (editable from the dashboard) are the fallback."""
    global _credentials_cache

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if token and chat_id:
        return token, chat_id, "env"

    now = time.monotonic()
    if _credentials_cache is not None and now - _credentials_cache[2] < _CREDENTIALS_CACHE_TTL:
        db_token, db_chat_id = _credentials_cache[0], _credentials_cache[1]
    else:
        db_token, db_chat_id = _read_db_credentials()
        _credentials_cache = (db_token, db_chat_id, now)

    token = token or db_token
    chat_id = chat_id or db_chat_id

    if token and chat_id:
        return token, chat_id, "database"

    return None, None, None


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

        token, chat_id, _ = get_telegram_credentials()

        if not token or not chat_id:
            if not _warned_unconfigured:
                _warned_unconfigured = True
                logging.warning(
                    "Telegram alerts not configured (set TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID "
                    "or save credentials from the dashboard's Alerts page)."
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
