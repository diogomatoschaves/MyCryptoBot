import json
import logging
import os
import sys
from distutils.util import strtobool

import redis
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required, JWTManager
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from model.service.cloud_storage import check_aws_config
from model.service.helpers.decorators.handle_app_errors import handle_app_errors
from model.service.helpers.responses import Responses
from model.strategies.properties import compile_strategies
from model.worker import conn
from shared.utils.config_parser import get_config
from shared.utils.decorators import handle_db_connection_error
from shared.utils.helpers import get_pipeline_data, get_item_from_cache
from shared.utils.logger import configure_logger


module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

config_vars = get_config('model')

configure_logger(os.getenv("LOGGER_LEVEL", config_vars.logger_level))
logging.getLogger('botocore').setLevel(logging.CRITICAL)

cache = redis.from_url(os.getenv('REDIS_URL', config_vars.redis_url))

q = Queue(connection=conn)


def create_app():

    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.getenv('SECRET_KEY')
    jwt = JWTManager(app)

    try:
        upload_files_s3 = bool(strtobool(os.getenv("USE_CLOUD_STORAGE", "false")))
    except ValueError:
        upload_files_s3 = False

    os.environ["USE_CLOUD_STORAGE"] = str(upload_files_s3 and check_aws_config())

    @app.route('/')
    @jwt_required()
    def hello_world():
        return "It's up!"

    @app.route('/generate_signal', methods=['POST'])
    @handle_app_errors
    @jwt_required()
    @handle_db_connection_error
    def generate_signal():

        bearer_token = request.headers.get('Authorization')

        request_data = request.get_json(force=True)

        logging.debug(request_data)

        pipeline_id = request_data.get("pipeline_id", None)

        pipeline = get_pipeline_data(pipeline_id)

        header = json.loads(get_item_from_cache(cache, pipeline_id))

        pipeline_dict = dict(
            id=pipeline.id,
            strategies=pipeline.strategy,
            strategy_combination=pipeline.strategy_combination,
            symbol=pipeline.symbol,
            exchange=pipeline.exchange,
            interval=pipeline.candle_size
        )

        job = q.enqueue_call(
            "model.signal_generation._signal_generation.signal_generator", (
                pipeline_dict,
                bearer_token,
                header
            )
        )

        job_id = job.get_id()

        return jsonify(Responses.SIGNAL_GENERATION_INPROGRESS(job_id))

    @app.route('/check_job/<job_id>', methods=['GET'])
    @jwt_required()
    @handle_db_connection_error
    def check_job(job_id):
        try:
            job = Job.fetch(job_id, connection=conn)
        except NoSuchJobError:
            logging.info(f"Job {job_id} not found.")
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
    @handle_db_connection_error
    def get_strategies():
        strategies = compile_strategies()
        return jsonify(strategies)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0')
