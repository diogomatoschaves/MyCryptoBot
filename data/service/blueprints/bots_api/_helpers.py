import logging
import os
import threading
import time
from datetime import datetime

import pytz
from concurrent.futures import ThreadPoolExecutor
from functools import reduce

import redis
from django.db import close_old_connections

from data.service.external_requests import start_stop_symbol_trading
from data.sources._sources import DataHandler
from shared.exchanges.binance import BinanceHandler
from shared.utils.events import publish_pipeline_event, EVENT_STARTED, EVENT_START_FAILED
from shared.utils.notifier import send_alert
from shared.utils.settings import settings
from shared.utils.helpers import get_logging_row_header, add_pipeline_loading, is_pipeline_loading


cache = redis.from_url(settings.redis_url)
executor = ThreadPoolExecutor(16)

binance_instances = []

# guards the rebuild-and-reassign of binance_instances: with gthread workers
# plus the health-cron thread, concurrent stop/start could lose each other's
# update (resurrecting a stopped handler or dropping a live one)
_instances_lock = threading.Lock()

binance_client = BinanceHandler()


def initialize_data_collection(pipeline, header):

    global binance_instances

    data_handler = DataHandler(pipeline, header=header)
    with _instances_lock:
        binance_instances.append(data_handler.binance_handler)
    data_handler.binance_handler.start_data_ingestion(header=header)


def _run_data_collection(pipeline, header):
    """
    Executor entrypoint for starting a pipeline's data collection. The bare
    task used to be fire-and-forget: an exception here died inside the
    thread pool, leaving the pipeline marked active in the database with no
    data flowing - a zombie 'Running' bot. Failures now deactivate the
    pipeline, clean up, alert and publish an event.
    """
    # executor threads are long-lived: drop any DB connection that exceeded
    # CONN_MAX_AGE so the failure path below cannot die on a stale connection
    close_old_connections()

    try:
        initialize_data_collection(pipeline, header)
    except Exception as e:
        logging.exception(header + f"Data collection for pipeline {pipeline.id} failed to start: {e}")

        # best effort: drop any partially registered local instance
        try:
            stop_instance(pipeline.id, header, force=True)
        except Exception:
            pass

        # best effort: clear the execution service's trader state (it accepted
        # the start before data collection began) so a retry isn't rejected
        # with SYMBOL_ALREADY_TRADED and any opened position is closed
        try:
            start_stop_symbol_trading(
                {
                    "paper_trading": pipeline.paper_trading,
                    "symbol": pipeline.symbol.name,
                    "force": True,
                },
                'stop',
            )
        except Exception:
            pass

        from database.model.models import Pipeline
        Pipeline.objects.filter(id=pipeline.id).update(active=False, open_time=None)

        send_alert(
            title="Pipeline failed to start",
            body=(
                f"Pipeline {pipeline.id} ('{pipeline.name}', {pipeline.symbol.name}): "
                f"data collection failed to start ({e}). The pipeline was deactivated."
            ),
            severity="critical",
            dedup_key=f"start-failed-{pipeline.id}",
        )
        publish_pipeline_event(EVENT_START_FAILED, pipeline.id, reason=str(e))


def reduce_instances(accumulator, instance, pipeline_id, header, raise_exception, force):

    if pipeline_id == instance.pipeline_id:
        return_value = instance.stop_data_ingestion(
            header=header,
            raise_exception=raise_exception,
            force=force,
        )
        return {
            **accumulator,
            "return_values": [*accumulator["return_values"], return_value]
        }

    else:
        return {
            **accumulator,
            "instances": [*accumulator["instances"], instance]
        }


def stop_instance(pipeline_id, header, raise_exception=False, force=False):

    global binance_instances

    with _instances_lock:
        reduced_instances = reduce(
            lambda accumulator, instance: reduce_instances(
                accumulator, instance, pipeline_id, header, raise_exception, force
            ),
            binance_instances,
            {"instances": [], "return_values": []}
        )

        binance_instances = reduced_instances["instances"]

    try:
        return reduced_instances["return_values"][0]
    except IndexError:
        return False


def stop_pipeline(pipeline_id, header='', raise_exception=False, nr_retries=3, force=False):
    success = stop_instance(pipeline_id, header, raise_exception, force=force)

    retries = 0
    while not success:
        if retries > nr_retries:
            break

        success = stop_instance(pipeline_id, header, raise_exception, force=True)

        retries += 1

        if not success:
            time.sleep(60 * retries)


def start_symbol_trading(pipeline, restart=False):

    add_pipeline_loading(cache, pipeline.id)

    payload = {
        "pipeline_id": pipeline.id,
        "binance_trader_type": "futures",
    }

    header = get_logging_row_header(cache, pipeline)

    logging.info(header + f"Starting data pipeline.")

    response = start_stop_symbol_trading(payload, 'start')

    # the execution service can in principle return null/short payloads
    # (e.g. an endpoint path without an explicit return) - never subscript
    # the response without guarding
    if not response:
        response = {
            "success": False,
            "code": "NO_RESPONSE",
            "message": "No response from the execution service.",
        }

    already_traded_on_restart = (
        response.get("code") == "SYMBOL_ALREADY_TRADED" and restart
    )

    if not response.get("success") and not already_traded_on_restart:
        pipeline.active = False
        pipeline.open_time = None
        pipeline.save(update_fields=["active", "open_time"])

        publish_pipeline_event(
            EVENT_START_FAILED, pipeline.id, reason=response.get("message")
        )

        return response
    else:
        response["success"] = True
        pipeline.last_entry = None
        if restart:
            # a restarted pipeline's never-ingested grace period must start
            # from now: keeping the old open_time would make the health check
            # flag it as stuck (last_entry=None + old open_time) right after
            # boot, before its first candle can possibly arrive
            pipeline.open_time = datetime.now(tz=pytz.utc)
        pipeline.save(update_fields=["last_entry", "open_time"])

    executor.submit(
        _run_data_collection,
        pipeline,
        header
    )

    publish_pipeline_event(EVENT_STARTED, pipeline.id)

    return response
