import json
import os
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import reduce

from flask import Flask, jsonify, request
import django
from flask_cors import CORS

import redis

from data.service.blueprints.dashboard import dashboard
from data.service.external_requests import start_stop_symbol_trading
from data.service.helpers.responses import Responses
from data.sources._sources import DataHandler
from shared.utils.helpers import get_logging_row_header, get_item_from_cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from data.service.helpers import check_input, get_or_create_pipeline
from database.model.models import Pipeline
from shared.utils.logger import configure_logger

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

executor = ThreadPoolExecutor(16)


app = Flask(__name__)
app.register_blueprint(dashboard)

CORS(app)

binance_instances = []

cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


def initialize_data_collection(pipeline):

    data_handler = DataHandler(pipeline)

    global binance_instances
    binance_instances.append(data_handler.binance_handler)


def reduce_instances(instances, instance, pipeline_id):
    if pipeline_id == instance.pipeline_id:
        instance.stop_data_ingestion()
        return instances
    else:
        return [*instances, instance]


def stop_instance(pipeline_id):

    global binance_instances

    binance_instances = reduce(
        lambda instances, instance: reduce_instances(instances, instance, pipeline_id),
        binance_instances,
        []
    )


@app.route('/')
def hello_world():
    return "I'm up!"


@app.route('/start_bot', methods=['PUT'])
def start_bot():

    data = request.get_json(force=True)

    symbol = data.get("symbol", None)
    strategy = data.get("strategy", None)
    params = data.get("params", {})
    candle_size = data.get("candleSize", None)
    exchange = data.get("exchanges", None)

    response = check_input(
        symbol=symbol,
        strategy=strategy,
        params=params,
        candle_size=candle_size,
        exchange=exchange
    )

    if response is not None:
        logging.debug(response)
        return response

    exchange = exchange.lower()
    candle_size = candle_size.lower()

    pipeline, response = get_or_create_pipeline(
        symbol=symbol,
        candle_size=candle_size,
        strategy=strategy,
        exchange=exchange,
        params=params,
    )

    if response is not None:
        logging.debug(response)
        return response

    cache.set(
        f"pipeline {pipeline.id}",
        json.dumps(get_logging_row_header(symbol, strategy, params, candle_size, exchange))
    )

    response = start_stop_symbol_trading(pipeline.id, 'start')

    if not response["success"]:
        logging.warning(response["response"])

        pipeline.active = False
        pipeline.save()

        return jsonify({"response": response["response"]})

    logging.info(json.loads(get_item_from_cache(cache, pipeline.id)) +
                 f"Starting data pipeline.")

    executor.submit(
        initialize_data_collection,
        pipeline
    )

    return jsonify(Responses.DATA_PIPELINE_START_OK(pipeline.id))


@app.route('/stop_bot', methods=['PUT'])
def stop_bot():

    # Stops the data collection stream
    # closes any open positions
    data = request.get_json(force=True)

    pipeline_id = data.get("pipeline_id", None)

    try:
        pipeline = Pipeline.objects.get(id=pipeline_id)

        logging.info(json.loads(get_item_from_cache(cache, pipeline_id)) + f"Stopping data pipeline.")

        stop_instance(pipeline_id)

        response = start_stop_symbol_trading(pipeline_id, 'stop')

        logging.debug(response["response"])

        pipeline.active = False
        pipeline.save()

        return jsonify(Responses.DATA_PIPELINE_STOPPED)
    except Pipeline.DoesNotExist:
        return jsonify(Responses.DATA_PIPELINE_INEXISTENT)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
