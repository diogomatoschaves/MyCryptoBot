import logging
import os
import sys

import django
from flask import Flask, jsonify, request
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from model.model import gen_signal
from model.worker import conn
from shared.utils.logger import configure_logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

app_name = os.getenv("APP_NAME")


app = Flask(__name__)

q = Queue(connection=conn)


strategies = [
    'BollingerBands',
    'MachineLearning',
    'Momentum',
    'MovingAverageConvergenceDivergence',
    'MovingAverage',
    'MovingAverageCrossover',
]


@app.route('/')
def hello_world():
    return "It's up!"


@app.route('/generate_signal', methods=['POST'])
def generate_signal():

    # Trigger data fetching
    # Generate signal
    # Send orders

    request_data = request.get_json(force=True)

    logging.debug(request_data)

    symbol = request_data.get("symbol", None)
    strategy = request_data.get("strategy", None)
    params = request_data.get("params", {})
    candle_size = request_data.get("candle_size", "1h")
    exchange = request_data.get("exchange", "binance")

    if strategy not in strategies:
        return jsonify({"response": f"Invalid {strategy} strategy.", "success": False})

    job = q.enqueue_call(gen_signal, (symbol, candle_size, exchange, strategy, params))

    job_id = job.get_id()

    Jobs.objects.create(job_id=job_id, app=app_name)

    return jsonify({"response": f"Signal generation process started", "success": True})


@app.route('/check_job/<job_id>', methods=['GET'])
def check_job(job_id):

    try:
        job = Job.fetch(job_id, connection=conn)
    except NoSuchJobError:
        return jsonify({"status": 'job not found'})

    if job.is_finished:

        return jsonify(job.result)

    elif job.is_queued:
        return jsonify({"status": 'in-queue'})

    elif job.is_started:
        return jsonify({"status": 'waiting'})

    elif job.is_failed:
        return jsonify({"status": 'failed'})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
