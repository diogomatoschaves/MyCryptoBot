import json
import logging
import os
import sys
from datetime import datetime, timedelta

import pytz
import redis
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required, JWTManager
from rq import Callback, Queue, Worker
from rq.exceptions import NoSuchJobError
from rq.job import Job

from model.service.cloud_storage import cloud_storage_startup
from model.service.helpers.decorators.handle_app_errors import handle_app_errors
from model.service.helpers.responses import Responses
from model.strategies.properties import compile_strategies
from model.worker import conn
import shared.exchanges.binance.constants as const
from shared.utils.settings import settings
from shared.utils.decorators import handle_db_connection_error
from shared.utils.helpers import get_pipeline_data, get_item_from_cache, get_jwt_secret_key
from shared.utils.logger import configure_logger
from shared.utils.notifier import send_alert


module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


configure_logger(settings.logger_level)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

cache = redis.from_url(settings.redis_url)

q = Queue(connection=conn)

# failed signal jobs stay inspectable in the FailedJobRegistry for a week
# (instead of rq's 1-year default) - see rq's failure_ttl
JOB_FAILURE_TTL = int(timedelta(days=7).total_seconds())

SIGNAL_FAILURE_CALLBACK = "model.signal_generation._signal_generation.signal_failure_handler"


def warn_if_no_workers():
    """A queued job with no worker will silently expire after its ttl - make
    the outage loud. The job is still enqueued: a worker may come back in time."""
    try:
        if Worker.count(queue=q) == 0:
            logging.warning("No active RQ workers - queued signal jobs will expire unprocessed.")
            send_alert(
                title="RQ worker down",
                body=(
                    "No active RQ workers on the model service - signal jobs are "
                    "being queued but will expire unprocessed unless a worker returns."
                ),
                severity="critical",
                dedup_key="rq-worker-down",
                throttle_seconds=900,
            )
            return True
    except Exception as e:
        logging.warning(f"Could not check RQ worker count: {e}")

    return False


def create_app():

    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = get_jwt_secret_key()
    jwt = JWTManager(app)

    cloud_storage_startup()

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

        # the job computes its own staleness deadline from this timestamp -
        # a late-starting job must discard the signal, not fire a stale order
        pipeline_dict["enqueued_at"] = datetime.now(tz=pytz.utc).isoformat()

        # a job that hasn't started within one candle period is superseded by
        # the next candle's job - discard it instead of firing a stale order
        ttl = int(timedelta(**const.CANDLE_SIZE_TIMEDELTA[pipeline.candle_size]).total_seconds())

        warn_if_no_workers()

        job = q.enqueue_call(
            "model.signal_generation._signal_generation.signal_generator", (
                pipeline_dict,
                bearer_token,
                header
            ),
            ttl=ttl,
            failure_ttl=JOB_FAILURE_TTL,
            on_failure=Callback(SIGNAL_FAILURE_CALLBACK),
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
            if warn_if_no_workers():
                logging.warning(
                    f"Job {job_id} not found and no RQ workers are running - probable worker outage."
                )
            else:
                logging.info(f"Job {job_id} not found.")
            return jsonify(Responses.JOB_NOT_FOUND)

        if job.is_finished:
            return jsonify(Responses.FINISHED(job.result))

        elif job.is_queued:
            return jsonify(Responses.IN_QUEUE)

        elif job.is_started or job.is_deferred or job.is_scheduled:
            return jsonify(Responses.WAITING)

        else:
            # failed, stopped, canceled or any unknown state: report failure
            # instead of returning None (which made callers wait forever)
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
