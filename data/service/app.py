import os
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import reduce

from django.db import IntegrityError
from flask import Flask, jsonify, request
import django
from flask_cors import CORS

from data.service.blueprints.dashboard import dashboard
from data.service.external_requests import start_stop_symbol_trading
from data.service.helpers.responses import Responses

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from data.service.helpers import check_input
from data.sources.binance import BinanceDataHandler
from database.model.models import Jobs
from shared.utils.logger import configure_logger

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

executor = ThreadPoolExecutor(16)


app = Flask(__name__)
app.register_blueprint(dashboard)

CORS(app)

binance_instances = []


def initialize_data_collection(strategy, params, symbol, candle_size):

    binance_handler = BinanceDataHandler(strategy, params, symbol, candle_size)

    binance_handler.start_data_ingestion()

    global binance_instances
    binance_instances.append(binance_handler)


def reduce_instances(instances, instance, symbol):
    if symbol == instance.symbol:
        instance.stop_data_ingestion()
        return instances
    else:
        return [*instances, instance]


def stop_instance(symbol):

    global binance_instances

    binance_instances = reduce(
        lambda instances, instance: reduce_instances(instances, instance, symbol),
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

    try:
        Jobs.objects.create(job_id=symbol, exchange_id=exchange.lower(), app=os.getenv("APP_NAME"))
        logging.info(f"Starting {symbol} Data pipeline.")
    except IntegrityError as e:
        logging.debug(e)
        return jsonify(Responses.DATA_PIPELINE_ONGOING(symbol))

    response = start_stop_symbol_trading(symbol, exchange, 'start')

    if not response["success"]:
        logging.warning(response["response"])
        return jsonify({"response": response["response"]})

    executor.submit(
        initialize_data_collection,
        strategy,
        params,
        symbol,
        candle_size
    )

    return jsonify(Responses.DATA_PIPELINE_START_OK(symbol))


@app.route('/stop_bot', methods=['PUT'])
def stop_bot():

    # Stops the data collection stream
    # closes any open positions
    data = request.get_json(force=True)

    symbol = data.get("symbol", None)
    exchange = data.get("exchange", None)

    response = check_input(symbol=symbol, exchange=exchange)

    if response is not None:
        return response

    try:
        job = Jobs.objects.get(job_id=symbol, exchange_id=exchange.lower(), app=os.getenv("APP_NAME"))

        logging.info(f"Stopping {symbol} data pipeline.")

        stop_instance(job.job_id)

        response = start_stop_symbol_trading(symbol, exchange, 'stop')

        logging.debug(response["response"])

        job.delete()

        return jsonify(Responses.DATA_PIPELINE_STOPPED(symbol))
    except Jobs.DoesNotExist:
        return jsonify(Responses.DATA_PIPELINE_INEXISTENT(symbol))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
