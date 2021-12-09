import json
import logging
import os
import sys

import django
import redis
from flask import Flask, jsonify, request
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from model.service.helpers.responses import Responses
from model.service.helpers.signal_generator import get_signal
from model.worker import conn
from shared.utils.helpers import get_pipeline_data, get_item_from_cache
from shared.utils.logger import configure_logger


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Jobs

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))


cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


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

    request_data = request.get_json(force=True)

    logging.debug(request_data)

    pipeline_id = request_data.get("pipeline_id", None)

    pipeline_exists, pipeline = get_pipeline_data(pipeline_id)

    if not pipeline_exists:
        return jsonify(Responses.NO_SUCH_PIPELINE(pipeline_id))

    header = json.loads(get_item_from_cache(cache, pipeline_id))

    job = q.enqueue_call(
        get_signal, (
            pipeline_id,
            pipeline.symbol,
            pipeline.candle_size,
            pipeline.exchange,
            pipeline.strategy,
            pipeline.params,
            header
        )
    )

    job_id = job.get_id()

    Jobs.objects.create(job_id=job_id, exchange_id=pipeline.exchange, app=os.getenv("APP_NAME"))

    return jsonify(Responses.SIGNAL_GENERATION_INPROGRESS(job_id))


@app.route('/check_job/<job_id>', methods=['GET'])
def check_job(job_id):
    try:
        job = Job.fetch(job_id, connection=conn)
    except NoSuchJobError:
        return jsonify(Responses.JOB_NOT_FOUND)

    if job.is_finished:
        return jsonify(Responses.FINISHED(job.result))

    elif job.is_queued:
        return jsonify(Responses.IN_QUEUE)

    elif job.is_started:
        return jsonify(Responses.WAITING)

    elif job.is_failed:
        return jsonify(Responses.FAILED)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
