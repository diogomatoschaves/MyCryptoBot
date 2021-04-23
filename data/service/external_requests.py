import logging
import os

import requests

from data.service.helpers import MODEL_APP_ENDPOINTS, EXECUTION_APP_ENDPOINTS
from shared.utils.decorators.failed_connection import retry_failed_connection


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
def generate_signal(symbol, strategy, params, candle_size, exchange):

    url = MODEL_APP_ENDPOINTS["GENERATE_SIGNAL"](os.getenv("MODEL_APP_URL"))

    payload = prepare_payload(
        symbol=symbol,
        strategy=strategy,
        params=params,
        candle_size=candle_size,
        exchange=exchange,
    )

    logging.info(
        f"{symbol}: Sending signal: " +
        ", ".join([f"{key}: {value}" for key, value in payload.items()])
    )

    r = requests.post(url, json=payload)
    logging.debug(r.text)

    response = r.json()
    logging.debug(response["response"])

    return response


@retry_failed_connection(num_times=2)
def start_stop_symbol_trading(symbol, exchange, start_or_stop):

    endpoint = f"{start_or_stop.upper()}_SYMBOL_TRADING"

    url = EXECUTION_APP_ENDPOINTS[endpoint](os.getenv("EXECUTION_APP_URL"))

    payload = {
        "symbol": symbol,
        "exchange": exchange
    }

    r = requests.post(url, json=payload)
    logging.debug(r.text)

    response = r.json()
    logging.debug(response["response"])

    return response
