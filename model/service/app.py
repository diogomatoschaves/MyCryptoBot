import json
import logging
import os
import sys

import redis
from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required, JWTManager
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from model.service.helpers.decorators.handle_app_errors import handle_app_errors
from model.service.helpers.responses import Responses
from model.service.helpers.signal_generator import get_signal
from model.strategies.properties import STRATEGIES
from model.worker import conn
from shared.utils.helpers import get_pipeline_data, get_item_from_cache
from shared.utils.logger import configure_logger


module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))


cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
jwt = JWTManager(app)

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
@jwt_required()
def hello_world():
    return "It's up!"


@app.route('/generate_signal', methods=['POST'])
@handle_app_errors
@jwt_required()
def generate_signal():

    bearer_token = request.headers.get('Authorization')

    request_data = request.get_json(force=True)

    logging.debug(request_data)

    pipeline_id = request_data.get("pipeline_id", None)

    pipeline = get_pipeline_data(pipeline_id)

    header = json.loads(get_item_from_cache(cache, pipeline_id))

    job = q.enqueue_call(
        get_signal, (
            pipeline_id,
            pipeline.symbol,
            pipeline.candle_size,
            pipeline.exchange,
            pipeline.strategy,
            pipeline.params,
            bearer_token,
            header
        )
    )

    job_id = job.get_id()

    return jsonify(Responses.SIGNAL_GENERATION_INPROGRESS(job_id))


@app.route('/check_job/<job_id>', methods=['GET'])
@jwt_required()
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


@app.route('/strategies', methods=['GET'])
@jwt_required()
def get_strategies():
    return jsonify(STRATEGIES)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
