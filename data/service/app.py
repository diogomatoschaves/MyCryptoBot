import os
import logging
import sys
from concurrent.futures import ThreadPoolExecutor

from django.db import IntegrityError
from flask import Flask, jsonify, request
import django

from data.service.helpers import STRATEGIES

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from data.sources.binance import BinanceDataHandler
from database.model.models import Jobs, Symbol
from shared.utils.logger import configure_logger

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

executor = ThreadPoolExecutor(16)

app_name = os.getenv("APP_NAME")

app = Flask(__name__)

binance_instances = []


def initialize_data_collection(strategy, params, symbol, candle_size):
    global binance_instances

    binance_handler = BinanceDataHandler(strategy, params, symbol, candle_size)

    binance_handler.start_data_ingestion()

    binance_instances.append(binance_handler)


def stop_instance(instance_symbol):
    global binance_instances

    new_binance_instances = []
    for instance in binance_instances:

        if instance_symbol == instance.symbol:
            instance.stop_data_ingestion()
        else:
            new_binance_instances.append(instance)

    binance_instances = new_binance_instances


def check_input(symbol, strategy, params, candle_size):

    if not symbol:
        return jsonify({"response": "A symbol must be included in the request."})

    try:
        Symbol.objects.get(name=symbol)
    except Symbol.DoesNotExist:
        return jsonify({"response": f"{symbol} is not a valid symbol."})

    try:
        Jobs.objects.create(job_id=f"{symbol}", app=app_name)
        logging.info(f"Starting {symbol} Data pipeline.")
    except IntegrityError:
        logging.info(f"Requested {symbol} data pipeline already exists.")
        return jsonify({"response": f"{symbol} data pipeline already ongoing."})

    if strategy in STRATEGIES:
        for key in params:
            if key not in STRATEGIES[strategy]["params"]:
                return jsonify({"response": f"Provided {key} in params is not valid."})
    else:
        return jsonify({"response": f"{strategy} is not a valid strategy."})

    return None


@app.route('/')
def hello_world():
    return "I'm up!"


@app.route('/start_bot', methods=['PUT'])
def start_bot():

    data = request.get_json(force=True)

    symbol = data.get("symbol", None)
    strategy = data.get("strategy", None)
    params = data.get("params", {})
    candle_size = data.get("candle_size", "1h")

    response = check_input(symbol, strategy, params, candle_size)

    if response is not None:
        return response

    executor.submit(
        initialize_data_collection,
        strategy,
        params,
        symbol,
        candle_size
    )

    return jsonify({"response": f"{symbol} data pipeline successfully started."})


@app.route('/stop_bot', methods=['PUT'])
def stop_bot():

    # Stops the data collection stream
    # closes any open positions
    data = request.get_json(force=True)
    symbol = data.get("symbol", None)

    if not symbol:
        return jsonify({"response": "A symbol must be included in the request."})

    if Jobs.objects.filter(job_id=symbol, app=app_name).exists():
        logging.info(f"Stopping {symbol} data pipeline.")

        job = Jobs.objects.get(app=app_name)

        stop_instance(job.job_id)

        job.delete()

        return jsonify({"response": f"{symbol} data pipeline stopped."})

    else:
        return jsonify({"response": f"There is no {symbol} active data pipeline."})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
