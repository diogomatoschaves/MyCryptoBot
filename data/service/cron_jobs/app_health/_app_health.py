import logging
import os
import datetime
from distutils.util import strtobool

import django
import pytz

from data.service.blueprints.bots_api import stop_pipeline, start_symbol_trading
from data.service.external_requests import get_open_positions, start_stop_symbol_trading
from shared.utils.config_parser import get_config
from shared.utils.decorators import handle_db_connection_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline, Position


config = get_config()


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
    if strtobool(config.restart_failed_pipelines) and pipeline.restarted < int(config.restart_retries):

        logging.info(f"Restarting pipeline {pipeline.id}...")

        start_symbol_trading(pipeline)

        pipeline.restarted += 1
        pipeline.open_time = datetime.datetime.now(pytz.utc)
        pipeline.active = True
        pipeline.save()


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

    if pipeline.last_entry and now - pipeline.last_entry > datetime.timedelta(minutes=10):

        logging.info(f'Pipeline {pipeline.id} found to be stuck. Sending stop request...')
        stop_pipeline(pipeline.id, '', raise_exception=False)

        return True


def check_matching_remote_position(positions, pipeline):
    """
    Verifies if there is a matching position on the remote trading platform
    for the given pipeline's symbol. If not, the pipeline is stopped.

    Parameters
    ----------
    positions : dict
        A dictionary containing lists of positions for each account type (e.g., "testnet" and "live").
    pipeline : Pipeline object
        The pipeline object to check, which includes the trading symbol and
        whether it's for paper trading or live trading.

    Notes
    -----
    - This function checks if the remote trading platform has an open position that matches the pipeline's symbol.
    - If no matching position is found for the active pipeline, a stop request is sent for the pipeline,
        and the balance is restored
    """
    logging.debug(f'Checking if pipeline {pipeline.id} has a corresponding remote position...')

    account = 'testnet' if pipeline.paper_trading else 'live'

    position = find_position(positions[account], pipeline.symbol.name)

    td = datetime.datetime.now(pytz.utc) - pipeline.open_time

    if td > datetime.timedelta(minutes=5) and position is None:

        logging.info(f'Remote position for pipeline {pipeline.id} not found. Stopping pipeline...')

        stop_pipeline(pipeline.id, '', raise_exception=False, force=True)

        # Restore balance of pipeline
        pipeline.active = False
        pipeline.units = 0
        pipeline.balance = pipeline.current_equity * pipeline.leverage
        pipeline.save()

        Position.objects.filter(pipeline__id=pipeline.id).update(position=0)

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

    for pipeline in active_pipelines:

        restart1 = check_pipeline_stuck(pipeline)

        restart2 = check_matching_remote_position(positions, pipeline)

        if restart1 or restart2:
            restart_pipeline(pipeline)


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

    # Get open positions
    response = get_open_positions()

    if not response["success"]:
        logging.info('Could not retrieve open positions.')
        return

    positions = response["positions"]

    if strtobool(config.check_inconsistencies):
        check_inconsistencies(positions)

    check_active_pipelines(positions)

    logging.info('App health check complete.')
