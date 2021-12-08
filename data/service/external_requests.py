import json
import logging
import os

import redis
import requests

from data.service.helpers import MODEL_APP_ENDPOINTS, EXECUTION_APP_ENDPOINTS
from shared.utils.decorators import retry_failed_connection, json_error_handler
from shared.utils.helpers import get_item_from_cache

cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


def prepare_payload(**kwargs):
    return {key: value for key, value in kwargs.items()}


@retry_failed_connection(num_times=1)
def check_job_status(job_id):
    url = MODEL_APP_ENDPOINTS["CHECK_JOB"](os.getenv("MODEL_APP_URL"), job_id)

    r = requests.get(url)
    logging.debug(r.text)

    response = r.json()
    logging.debug(f"{job_id}: {response}")

    return response


@retry_failed_connection(num_times=2)
@json_error_handler
def generate_signal(pipeline_id):

    url = MODEL_APP_ENDPOINTS["GENERATE_SIGNAL"](os.getenv("MODEL_APP_URL"))

    payload = prepare_payload(
        pipeline_id=pipeline_id
    )

    logging.info(
        json.loads(get_item_from_cache(cache, pipeline_id)) + "Triggering signal"
    )

    r = requests.post(url, json=payload)
    logging.debug(r.text)

    response = r.json()
    logging.debug(response["response"])

    return response


@retry_failed_connection(num_times=2)
@json_error_handler
def start_stop_symbol_trading(pipeline_id, start_or_stop):

    endpoint = f"{start_or_stop.upper()}_SYMBOL_TRADING"

    url = EXECUTION_APP_ENDPOINTS[endpoint](os.getenv("EXECUTION_APP_URL"))

    payload = {
        "pipeline_id": pipeline_id,
    }

    r = requests.post(url, json=payload)
    logging.debug(r.text)

    response = r.json()
    logging.debug(response["response"])

    return response
