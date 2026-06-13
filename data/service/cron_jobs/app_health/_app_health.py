import logging
import os
import datetime

import django
import pytz
import redis
from django.db import close_old_connections

from data.service.blueprints.bots_api import stop_pipeline, start_symbol_trading
from data.service.external_requests import get_open_positions, start_stop_symbol_trading
from shared.utils.settings import settings
from shared.utils.decorators import handle_db_connection_error
from shared.utils.events import publish_pipeline_event, EVENT_STARTED, EVENT_DEACTIVATED, EVENT_START_FAILED
from shared.utils.notifier import send_alert
from shared.utils.helpers import is_pipeline_loading

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline, Position



cache = redis.from_url(settings.redis_url)

# 3 missed base candles (5m): short websocket hiccups recover on their own,
# anything longer warrants a stop + restart attempt
STUCK_THRESHOLD = datetime.timedelta(minutes=15)

# grace period before a missing remote position counts as a mismatch - must
# stay larger than CHECKS_INTERVAL so a just-(re)started pipeline whose first
# order is still settling is never force-stopped by the very next check
POSITION_MISMATCH_GRACE = datetime.timedelta(minutes=15)

# a pipeline healthy for this long after a restart gets its retry budget
# back: restart_retries means "retries per incident", not "per lifetime"
RESTART_COUNTER_RESET_AFTER = datetime.timedelta(hours=1)

# budget for the initial historical data load (the redis loading flag has no
# TTL, so a crash mid-load must not hide a pipeline forever)
INITIAL_DATA_TIMEOUT = datetime.timedelta(hours=1)


def pipeline_label(pipeline):
    symbol = getattr(pipeline.symbol, "name", "?")
    mode = "paper" if pipeline.paper_trading else "LIVE"
    return f"Pipeline {pipeline.id} ('{pipeline.name}', {symbol}, {mode})"


def find_position(positions, symbol):
    """
    Searches for a trading position matching a given symbol within a list of positions.

    Parameters
    ----------
    positions : list of dict
        A list where each dictionary represents a trading position with key-value pairs.
    symbol : str
        The trading symbol to search for within the positions list.

    Returns
    -------
    dict or None
        The dictionary representing the found position, or None if no matching position is found.
    """
    for position in positions:
        if symbol == position["symbol"]:
            return position

    return None


def restart_pipeline(pipeline):
    if not settings.restart_failed_pipelines:
        return

    if pipeline.restarted >= settings.restart_retries:
        send_alert(
            title="Pipeline restart retries exhausted",
            body=(
                f"{pipeline_label(pipeline)}: restart retries exhausted "
                f"({pipeline.restarted}/{settings.restart_retries}). The pipeline "
                f"stays stopped - manual intervention required."
            ),
            severity="critical",
            dedup_key=f"restart-exhausted-{pipeline.id}",
            throttle_seconds=1800,
        )
        publish_pipeline_event(
            EVENT_DEACTIVATED, pipeline.id,
            reason=(
                f"restart retries exhausted "
                f"({pipeline.restarted}/{settings.restart_retries}) - manual restart required"
            ),
        )
        return

    logging.info(f"Restarting pipeline {pipeline.id}...")

    response = start_symbol_trading(pipeline, restart=True)

    if not response or not response["success"]:
        logging.warning(f"Pipeline {pipeline.id} could not be restarted.")
        send_alert(
            title="Pipeline restart attempt failed",
            body=(
                f"{pipeline_label(pipeline)}: restart attempt "
                f"{pipeline.restarted + 1} of {settings.restart_retries} failed"
                f"{': ' + str(response.get('message')) if response else ''}."
            ),
            severity="critical",
            dedup_key=f"restart-failed-{pipeline.id}",
        )
        publish_pipeline_event(
            EVENT_START_FAILED, pipeline.id,
            reason=f"restart attempt {pipeline.restarted + 1} of {settings.restart_retries} failed",
        )
        return

    Pipeline.objects.filter(id=pipeline.id).update(
        restarted=pipeline.restarted + 1,
        open_time=datetime.datetime.now(pytz.utc),
        active=True,
    )

    send_alert(
        title="Pipeline restarted",
        body=(
            f"{pipeline_label(pipeline)}: restart attempt "
            f"{pipeline.restarted + 1} of {settings.restart_retries} succeeded."
        ),
        severity="info",
        dedup_key=f"restart-ok-{pipeline.id}",
    )
    publish_pipeline_event(EVENT_STARTED, pipeline.id, restarted=True)


def check_pipeline_stuck(pipeline):
    """
    Checks if a trading pipeline is stuck based on the time elapsed since its last entry.
    If it is determined to be stuck, a stop request is sent.

    Parameters
    ----------
    pipeline : Pipeline object
        The trading pipeline object to be checked, which includes attributes like `id` and `last_entry`.

    Notes
    -----
    - A pipeline is considered stuck if the current time minus its `last_entry` timestamp
        is greater than a predefined threshold (e.g., 10 minutes).
    """
    logging.debug(f'Checking if pipeline {pipeline.id} is stuck...')

    now = datetime.datetime.now(pytz.utc)

    stuck_reason = None

    if pipeline.last_entry:
        if now - pipeline.last_entry > STUCK_THRESHOLD:
            minutes_stuck = int((now - pipeline.last_entry).total_seconds() // 60)
            stuck_reason = f"no candle entry for {minutes_stuck} minutes"
    elif pipeline.open_time:
        # the pipeline was started but never produced a single entry - this
        # used to escape the watchdog entirely (zombie 'Running' bots)
        age = now - pipeline.open_time

        try:
            loading = is_pipeline_loading(cache, pipeline.id)
        except Exception:
            # missing/unreadable loading flag must never hide a zombie
            loading = False

        if not loading and age > STUCK_THRESHOLD:
            stuck_reason = (
                f"started {int(age.total_seconds() // 60)} minutes ago "
                f"but never ingested any data"
            )
        elif loading and age > INITIAL_DATA_TIMEOUT:
            stuck_reason = (
                f"initial data load still incomplete after "
                f"{int(age.total_seconds() // 60)} minutes"
            )

    if stuck_reason:

        logging.info(f'Pipeline {pipeline.id} found to be stuck ({stuck_reason}). Sending stop request...')
        stop_pipeline(pipeline.id, '', raise_exception=False)

        send_alert(
            title="Stuck pipeline stopped",
            body=(
                f"{pipeline_label(pipeline)}: {stuck_reason} - stopped; "
                f"a restart will be attempted."
            ),
            severity="warning",
            dedup_key=f"stuck-{pipeline.id}",
        )
        publish_pipeline_event(
            EVENT_DEACTIVATED, pipeline.id,
            reason=f"{stuck_reason}; restart will be attempted",
        )

        return True


def check_matching_remote_position(positions, pipeline, already_stopped=False):
    """
    Verifies if there is a matching position on the remote trading platform
    for the given pipeline's symbol. If not, the pipeline is stopped (unless
    `already_stopped`, e.g. by the stuck check on the same pass) and the
    mismatch cleanup - balance restore, units and Position reset - runs.

    The cleanup must run even when another check already stopped the
    pipeline: it is the only place this state is repaired, and once the
    pipeline is inactive it leaves the active queryset for good.

    Parameters
    ----------
    positions : dict
        A dictionary containing lists of positions for each account type (e.g., "testnet" and "live").
    pipeline : Pipeline object
        The pipeline object to check, which includes the trading symbol and
        whether it's for paper trading or live trading.
    already_stopped : bool
        True when a previous check on this pass already stopped the
        pipeline - skips the duplicate stop call but not the cleanup.
    """
    logging.debug(f'Checking if pipeline {pipeline.id} has a corresponding remote position...')

    account = 'testnet' if pipeline.paper_trading else 'live'

    position = find_position(positions[account], pipeline.symbol.name)

    # an active pipeline without an open_time is anomalous - there is no
    # grace basis to wait on, so treat the grace period as elapsed
    grace_elapsed = (
        pipeline.open_time is None
        or datetime.datetime.now(pytz.utc) - pipeline.open_time > POSITION_MISMATCH_GRACE
    )

    # a pipeline whose strategy is in a neutral state legitimately has no
    # remote position - only flag a mismatch when the local position is open
    local_position_open = Position.objects.filter(
        pipeline__id=pipeline.id, position__in=[1, -1]
    ).exists()

    if grace_elapsed and position is None and local_position_open:

        logging.info(f'Remote position for pipeline {pipeline.id} not found. Stopping pipeline...')

        if not already_stopped:
            stop_pipeline(pipeline.id, '', raise_exception=False, force=True)

        restored_balance = pipeline.current_equity * pipeline.leverage

        # Restore balance of pipeline
        Pipeline.objects.filter(id=pipeline.id).update(
            active=False,
            units=0,
            balance=restored_balance,
        )

        Position.objects.filter(pipeline__id=pipeline.id).update(position=0)

        send_alert(
            title="Position mismatch - pipeline stopped",
            body=(
                f"{pipeline_label(pipeline)}: local records show an open position "
                f"but the {account} account has none. The pipeline was force-stopped "
                f"and its balance restored to {restored_balance:.2f}."
            ),
            severity="critical",
            dedup_key=f"mismatch-{pipeline.id}",
        )
        publish_pipeline_event(
            EVENT_DEACTIVATED, pipeline.id,
            reason=(
                f"position mismatch: local records show an open position but the "
                f"{account} account has none - stopped and balance restored"
            ),
        )

        return True


def check_active_pipelines(positions):
    """
    Iterates through all active pipelines, checking each for being stuck and for matching remote positions.

    Parameters
    ----------
    positions : dict
        A dictionary containing lists of positions for each account type (e.g., "testnet" and "live").

    Notes
    -----
    - Retrieves all active pipelines from the database and performs checks for each
    to ensure they are not stuck and have corresponding remote positions.
    - Utilizes `check_pipeline_stuck` and `check_matching_remote_position` functions for the checks.
    """
    active_pipelines = Pipeline.objects.filter(active=True)

    now = datetime.datetime.now(pytz.utc)

    for pipeline in active_pipelines:

        # one broken pipeline row must never abort the checks for the rest
        try:
            restart1 = check_pipeline_stuck(pipeline)

            # the mismatch check still runs when the stuck check already
            # stopped the pipeline: its cleanup (balance restore, Position
            # reset) is unique and this is the last pass that can apply it -
            # only the duplicate stop call is skipped
            restart2 = check_matching_remote_position(
                positions, pipeline, already_stopped=bool(restart1)
            )

            if restart1 or restart2:
                restart_pipeline(pipeline)
            elif (
                pipeline.restarted > 0
                and pipeline.open_time
                and now - pipeline.open_time > RESTART_COUNTER_RESET_AFTER
            ):
                # healthy for a sustained period after a restart: give the retry
                # budget back so unrelated incidents don't exhaust it over time
                Pipeline.objects.filter(id=pipeline.id).update(restarted=0)
        except Exception as e:
            logging.exception(f"Health check failed for pipeline {pipeline.id}: {e}")
            send_alert(
                title="Health check failed for a pipeline",
                body=f"{pipeline_label(pipeline)}: {e!r} - other pipelines were still checked.",
                severity="warning",
                dedup_key=f"health-error-{pipeline.id}",
            )


def check_inconsistencies(positions):
    """
    Checks for inconsistencies between local active pipeline positions and remote
    open positions. Closes any unmatched remote positions.

    Parameters
    ----------
    positions : dict
        A dictionary containing lists of positions for each account type (e.g., "testnet" and "live").

    Notes
    -----
    - For each position in both "testnet" and "live" accounts, checks if there
    exists a corresponding active pipeline with a matching symbol.
    - If an active pipeline does not exist for an open position, sends a request
    to close the remote position for that symbol.
    """
    for account in ["testnet", "live"]:
        for position in positions[account]:

            paper_trading = account == "testnet"

            # Check if positions match
            if not Pipeline.objects.filter(
                symbol=position["symbol"],
                paper_trading=paper_trading,
                active=True
            ).exists():
                payload = {
                    "paper_trading": paper_trading,
                    "force": True,
                    "symbol": position["symbol"]
                }

                logging.info(f'No active pipeline found matching {position["symbol"]} position. '
                             f'Closing {position["symbol"]} position...')

                send_alert(
                    title="Orphaned exchange position - closing",
                    body=(
                        f"{position['symbol']} ({account}): an open exchange position "
                        f"has no matching active pipeline. Closing the remote position."
                    ),
                    severity="critical",
                    dedup_key=f"orphan-{account}-{position['symbol']}",
                )

                # Close remote position for symbol
                start_stop_symbol_trading(payload, 'stop')


@handle_db_connection_error
def check_app_health():
    """
    Main function to check the application's status by verifying open positions and active pipelines
    for any inconsistencies.

    Notes
    -----
    - Retrieves open positions from a remote source and performs checks for inconsistencies
    with local pipeline statuses.
    - Utilizes `check_inconsistencies` and `check_active_pipelines` to ensure the trading
    application is running correctly and taking appropriate actions if issues are detected.
    """
    logging.info('Checking app health...')

    # Get open positions - a raised connection error must not kill the
    # scheduler job, and an unreachable execution service is alert-worthy
    try:
        response = get_open_positions()
    except Exception as e:
        response = None
        logging.warning(f'Could not retrieve open positions: {e}')

    if not response or not response["success"]:
        logging.info('Could not retrieve open positions.')
        send_alert(
            title="Execution service unreachable",
            body=(
                "Could not retrieve open positions from the execution service - "
                "health checks are degraded until it responds again."
            ),
            severity="warning",
            dedup_key="execution-unreachable",
            throttle_seconds=1800,
        )
        return

    positions = response["positions"]

    # the scheduler thread is long-lived: refresh DB connections past
    # CONN_MAX_AGE before the DB-touching checks below
    close_old_connections()

    if settings.check_inconsistencies:
        check_inconsistencies(positions)

    check_active_pipelines(positions)

    logging.info('App health check complete.')
