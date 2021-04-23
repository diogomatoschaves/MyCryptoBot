import logging
import os

import requests

from model.service.helpers import EXECUTION_APP_ENDPOINTS
from shared.utils.decorators.failed_connection import retry_failed_connection


@retry_failed_connection(num_times=3)
def execute_order(symbol, signal, exchange):

    url = EXECUTION_APP_ENDPOINTS["EXECUTE_ORDER"](os.getenv("EXECUTION_APP_URL"), exchange)

    payload = {
        "symbol": symbol,
        "signal": signal,
    }

    position = "GO LONG" if signal == 1 else "GO SHORT" if signal == -1 else "GO NEUTRAL"

    logging.info(f"{symbol}: Sending {position} order to {exchange}.")

    r = requests.post(url, json=payload)
    logging.debug(r.text)

    response = r.json()
    logging.debug(response["response"])

    return response
