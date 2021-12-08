import json
import logging
import os

import redis
import requests

from model.service.helpers import EXECUTION_APP_ENDPOINTS
from shared.utils.decorators.failed_connection import retry_failed_connection
from shared.utils.helpers import get_item_from_cache

cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


@retry_failed_connection(num_times=3)
def execute_order(pipeline_id, signal):

    url = EXECUTION_APP_ENDPOINTS["EXECUTE_ORDER"](os.getenv("EXECUTION_APP_URL"))

    payload = {
        "pipeline_id": pipeline_id,
        "signal": signal,
    }

    position = "GO LONG" if signal == 1 else "GO SHORT" if signal == -1 else "GO NEUTRAL"

    logging.info(json.loads(get_item_from_cache(cache, pipeline_id)) + f"Sending {position} order.")

    r = requests.post(url, json=payload)
    logging.debug(r.text)

    response = r.json()
    logging.debug(response["response"])

    return response
