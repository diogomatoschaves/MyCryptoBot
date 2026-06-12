"""Single source of configuration, driven by environment variables with
typed defaults. Replaces proj.conf + the cwd-walking config parser.

Every value is read from the environment once at import; the defaults match
the values that used to live in proj.conf, so behaviour is unchanged when no
env var is set.
"""
import os


def _strtobool(value):
    # distutils.util.strtobool replacement (distutils removed in Python 3.12)
    return str(value).strip().lower() in ("1", "true", "yes", "y", "t", "on")


def _get_str(env_var, default):
    return os.getenv(env_var, default)


def _get_int(env_var, default):
    value = os.getenv(env_var)
    return int(value) if value is not None else default


def _get_bool(env_var, default):
    value = os.getenv(env_var)
    return _strtobool(value) if value is not None else default


class Settings:

    def __init__(self):
        # [general]
        self.redis_url = _get_str("REDIS_URL", "redis://localhost:6379")
        self.default_min_rows = _get_int("DEFAULT_MIN_ROWS", 1000)
        self.check_inconsistencies = _get_bool("CHECK_INCONSISTENCIES", True)
        self.restart_failed_pipelines = _get_bool("RESTART_FAILED_PIPELINES", True)
        self.restart_retries = _get_int("RESTART_RETRIES", 2)

        # logging (per-service, but always overridable via LOGGER_LEVEL)
        self.logger_level = _get_str("LOGGER_LEVEL", "INFO")

        # [data]
        self.token_expires_days = _get_int("TOKEN_EXPIRES_DAYS", 3)
        self.app_check_interval_seconds = _get_int("CHECKS_INTERVAL", 300)
        self.base_candle_size = _get_str("BASE_CANDLE_SIZE", "5m")

        # [execution]
        self.app_snapshot_interval_seconds = _get_int("SNAPSHOTS_INTERVAL", 300)


settings = Settings()
