import json
import logging
import os
import time

import redis

from data.service.external_requests import generate_signal, check_job_status
from shared.utils.exceptions import FailedSignalGeneration
from shared.utils.helpers import get_item_from_cache

cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


# TODO: Implement logic to send this request
#  only if all data sources have updated the new row.
def trigger_signal(pipeline_id, retry=0):

    if retry > 2:

        raise FailedSignalGeneration(
            json.loads(get_item_from_cache(cache, pipeline_id)) +
            "Reached maximum number of attempts to trigger new signal."
        )

    response = generate_signal(pipeline_id)

    if "success" in response and response["success"]:
        return wait_for_job_conclusion(response["job_id"], pipeline_id, retry)
    else:
        logging.info(response["response"])
        return False


def wait_for_job_conclusion(job_id, pipeline_id, retry):

    retries = 0
    while True:

        response = check_job_status(job_id)

        if "status" in response:
            if response["status"] == "job not found":
                return trigger_signal(pipeline_id, retry=retry+1)
            elif response["status"] == "finished":
                logging.debug(json.loads(get_item_from_cache(cache, pipeline_id)) + f"Job {job_id} finished successfully.")
                return True
            elif response["status"] in ["in-queue", "waiting"]:
                time.sleep(5)
                retries += 1
            elif response["status"] == "failed":
                return False

        if retries > 40:
            return False