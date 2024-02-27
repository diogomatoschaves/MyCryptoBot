import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from functools import reduce

import django
import redis
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from data.service.external_requests import get_strategies, start_stop_symbol_trading
from data.service.helpers import check_input, get_or_create_pipeline, extract_request_params, convert_client_request
from shared.utils.config_parser import get_config
from shared.utils.decorators import general_app_error
from data.service.helpers.decorators.handle_app_errors import handle_app_errors
from data.service.helpers.exceptions import PipelineStartFail, DataPipelineDoesNotExist
from data.service.helpers.responses import Responses
from data.sources._sources import DataHandler
from shared.exchanges.binance import BinanceHandler
from shared.utils.decorators import handle_db_connection_error
from shared.utils.helpers import get_item_from_cache, get_logging_row_header

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline

config_vars = get_config()

cache = redis.from_url(os.getenv('REDIS_URL', config_vars.redis_url))

bots_api = Blueprint('bots_api', __name__)

executor = ThreadPoolExecutor(16)

binance_instances = []

binance_client = BinanceHandler()


def initialize_data_collection(pipeline, header):

    global binance_instances

    data_handler = DataHandler(pipeline, header=header)
    binance_instances.append(data_handler.binance_handler)
    data_handler.binance_handler.start_data_ingestion(header=header)


def reduce_instances(accumulator, instance, pipeline_id, header, raise_exception):

    if pipeline_id == instance.pipeline_id:
        return_value = instance.stop_data_ingestion(header=header, raise_exception=raise_exception)
        return {
            **accumulator,
            "return_values": [*accumulator["return_values"], return_value]
        }

    else:
        return {
            **accumulator,
            "instances": [*accumulator["instances"], instance]
        }


def stop_instance(pipeline_id, header, raise_exception=False):

    global binance_instances

    reduced_instances = reduce(
        lambda accumulator, instance: reduce_instances(
            accumulator, instance, pipeline_id, header, raise_exception
        ),
        binance_instances,
        {"instances": [], "return_values": []}
    )

    binance_instances = reduced_instances["instances"]

    return reduced_instances["return_values"]


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


@bots_api.put('/start_bot')
@general_app_error
@handle_app_errors
@jwt_required()
@handle_db_connection_error
def start_bot():

    if "STRATEGIES" not in globals():
        STRATEGIES = get_strategies()
        globals()["STRATEGIES"] = STRATEGIES
    else:
        STRATEGIES = globals()["STRATEGIES"]

    request_data = extract_request_params(request)

    exists = check_input(STRATEGIES, **request_data)

    data = convert_client_request(request_data)

    pipeline = get_or_create_pipeline(
        exists,
        request_data["pipeline_id"],
        request_data["strategy"],
        data
    )

    response = start_symbol_trading(pipeline)

    if not response["success"]:
        raise PipelineStartFail(pipeline.id)

    return jsonify(Responses.DATA_PIPELINE_START_OK(pipeline))


@bots_api.put('/stop_bot')
@general_app_error
@handle_app_errors()
@jwt_required()
@handle_db_connection_error
def stop_bot():

    # Stops the data collection stream
    # closes any open positions

    data = request.get_json(force=True)

    pipeline_id = data.get("pipelineId", None)

    try:
        Pipeline.objects.filter(id=pipeline_id).exists()

        header = json.loads(get_item_from_cache(cache, pipeline_id))

        logging.info(header + f"Stopping pipeline {pipeline_id}.")

        stop_instance(pipeline_id, header=header, raise_exception=True)

        pipeline = Pipeline.objects.get(id=pipeline_id)
        pipeline.active = False
        pipeline.save()

        return jsonify(Responses.DATA_PIPELINE_STOPPED(pipeline))
    except Pipeline.DoesNotExist:
        raise DataPipelineDoesNotExist(pipeline_id)
