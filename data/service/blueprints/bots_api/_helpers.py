import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from functools import reduce

import redis

from data.service.external_requests import start_stop_symbol_trading
from data.sources._sources import DataHandler
from shared.exchanges.binance import BinanceHandler
from shared.utils.config_parser import get_config
from shared.utils.helpers import get_logging_row_header

config_vars = get_config()

cache = redis.from_url(os.getenv('REDIS_URL', config_vars.redis_url))
executor = ThreadPoolExecutor(16)

binance_instances = []

binance_client = BinanceHandler()


def initialize_data_collection(pipeline, header):

    global binance_instances

    data_handler = DataHandler(pipeline, header=header)
    binance_instances.append(data_handler.binance_handler)
    data_handler.binance_handler.start_data_ingestion(header=header)


def reduce_instances(accumulator, instance, pipeline_id, header, raise_exception, force):

    if pipeline_id == instance.pipeline_id:
        return_value = instance.stop_data_ingestion(header=header, raise_exception=raise_exception, force=force)
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


def stop_pipeline(pipeline_id, header='', raise_exception=False, nr_retries=3):
    success = stop_instance(pipeline_id, header, raise_exception)

    retries = 0
    while not success:
        if retries > nr_retries:
            break

        success = stop_instance(pipeline_id, header, raise_exception, force=True)

        retries += 1

        if not success:
            time.sleep(60 * retries)


def start_symbol_trading(pipeline):
    payload = {
        "pipeline_id": pipeline.id,
        "binance_trader_type": "futures",
    }

    header = get_logging_row_header(cache, pipeline)

    logging.info(header + f"Starting data pipeline.")

    response = start_stop_symbol_trading(payload, 'start')

    if response["success"]:
        pipeline.last_entry = None
        pipeline.save()
    else:
        pipeline.active = False
        pipeline.open_time = None
        pipeline.save()

        return response

    executor.submit(
        initialize_data_collection,
        pipeline,
        header
    )

    return response
