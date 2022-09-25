import logging
import os

import requests

from data.service.helpers import MODEL_APP_ENDPOINTS, EXECUTION_APP_ENDPOINTS
from shared.utils.decorators import retry_failed_connection, json_error_handler


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
def generate_signal(pipeline_id, header=''):

    url = MODEL_APP_ENDPOINTS["GENERATE_SIGNAL"](os.getenv("MODEL_APP_URL"))

    payload = prepare_payload(
        pipeline_id=pipeline_id
    )

    logging.info(header + "Triggering signal")

    r = requests.post(url, json=payload)
    logging.debug(r.text)

    response = r.json()
    logging.debug(response["message"])

    return response


@retry_failed_connection(num_times=2)
@json_error_handler
def start_stop_symbol_trading(payload, start_or_stop):

    endpoint = f"{start_or_stop.upper()}_SYMBOL_TRADING"

    url = EXECUTION_APP_ENDPOINTS[endpoint](os.getenv("EXECUTION_APP_URL"))

    r = requests.post(url, json=payload)
    logging.debug(r.text)

    response = r.json()
    logging.debug(response["message"])

    return response


@retry_failed_connection(num_times=2)
@json_error_handler
def get_strategies():

    endpoint = "GET_STRATEGIES"

    url = MODEL_APP_ENDPOINTS[endpoint](os.getenv("MODEL_APP_URL"))

    r = requests.get(url)
    logging.debug("get_strategies: " + r.text)

    response = r.json()
    logging.debug(f"get_strategies: {response}")

    return response

