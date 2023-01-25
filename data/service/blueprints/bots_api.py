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
from data.service.helpers import check_input, get_or_create_pipeline
from data.service.helpers.decorators.handle_app_errors import handle_app_errors
from data.service.helpers.exceptions import PipelineStartFail, DataPipelineDoesNotExist
from data.service.helpers.responses import Responses
from data.sources._sources import DataHandler
from shared.exchanges import BinanceHandler
from shared.utils.decorators import handle_db_connection_error
from shared.utils.helpers import get_item_from_cache, get_logging_row_header

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline

cache = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

bots_api = Blueprint('bots_api', __name__)

executor = ThreadPoolExecutor(16)

binance_instances = []

binance_client = BinanceHandler()


def initialize_data_collection(pipeline, header):

    data_handler = DataHandler(pipeline, header=header)

    global binance_instances
    binance_instances.append(data_handler.binance_handler)


def reduce_instances(instances, instance, pipeline_id, header):
    if pipeline_id == instance.pipeline_id:
        instance.stop_data_ingestion(header=header)
        return instances
    else:
        return [*instances, instance]


def stop_instance(pipeline_id, header):

    global binance_instances

    binance_instances = reduce(
        lambda instances, instance: reduce_instances(instances, instance, pipeline_id, header),
        binance_instances,
        []
    )


def start_symbol_trading(pipeline):

    header = get_logging_row_header(pipeline)

    cache.set(
        f"pipeline {pipeline.id}",
        json.dumps(header)
    )

    logging.info(header + f"Starting data pipeline.")

    executor.submit(
        initialize_data_collection,
        pipeline,
        header
    )


@bots_api.put('/start_bot')
@handle_app_errors
@jwt_required()
@handle_db_connection_error
def start_bot():

    if "STRATEGIES" not in globals():
        STRATEGIES = get_strategies()
        globals()["STRATEGIES"] = STRATEGIES
    else:
        STRATEGIES = globals()["STRATEGIES"]

    data = request.get_json(force=True)

    pipeline_id = data.get("pipelineId", None)
    name = data.get("name", None)
    color = data.get("color", None)
    allocation = data.get("allocation", None)
    symbol = data.get("symbol", None)
    strategy = data.get("strategy", None)
    params = data.get("params", {})
    candle_size = data.get("candleSize", None)
    exchange = data.get("exchanges", None)
    paper_trading = data.get("paperTrading") if type(data.get("paperTrading")) == bool else False
    leverage = data.get("leverage", 1)

    exists = check_input(
        binance_client,
        STRATEGIES,
        pipeline_id=pipeline_id,
        name=name,
        color=color,
        allocation=allocation,
        symbol=symbol,
        strategy=strategy,
        params=params,
        candle_size=candle_size,
        exchange=exchange,
        leverage=leverage
    )

    exchange = exchange.lower()
    candle_size = candle_size.lower()

    pipeline = get_or_create_pipeline(
        exists,
        pipeline_id=pipeline_id,
        name=name,
        color=color,
        allocation=allocation,
        symbol=symbol,
        candle_size=candle_size,
        strategy=strategy,
        exchange=exchange,
        params=params,
        paper_trading=paper_trading,
        leverage=leverage
    )

    payload = {
        "pipeline_id": pipeline.id,
        "binance_trader_type": "futures",
    }

    response = start_stop_symbol_trading(payload, 'start')

    if not response["success"]:
        logging.warning(response["message"])

        pipeline.active = False
        pipeline.save()

        raise PipelineStartFail(response)

    start_symbol_trading(pipeline)

    return jsonify(Responses.DATA_PIPELINE_START_OK(pipeline))


@bots_api.put('/stop_bot')
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

        stop_instance(pipeline_id, header=header)

        pipeline = Pipeline.objects.get(id=pipeline_id)
        pipeline.active = False
        pipeline.save()

        return jsonify(Responses.DATA_PIPELINE_STOPPED(pipeline))
    except Pipeline.DoesNotExist:
        raise DataPipelineDoesNotExist(pipeline_id)
