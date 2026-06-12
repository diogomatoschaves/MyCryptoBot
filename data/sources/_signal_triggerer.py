import logging
import os
import time

import django
from requests import ReadTimeout, ConnectionError

from data.service.external_requests import generate_signal, check_job_status

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline


RESPONSES = {
    "PIPELINE_NOT_ACTIVE": (False, "Stopping Pipeline. Pipeline not active or does not exist."),
    "TOO_MANY_RETRIES": (False, "Stopping Pipeline. Too many retries."),
    "JOB_NOT_FOUND": (False, "Stopping Pipeline. Job not found."),
    "JOB_FAILED": (False, "Stopping Pipeline. Job failed."),
    "MODEL_APP_UNREACHABLE": (False, "Model app could not be reached."),
    "SUCCESS": (True, ""),
}


# TODO: Implement logic to send this request
#  only if all data sources have updated the new row.
def trigger_signal(pipeline_id, header='', retry=0):
    try:
        pipeline = Pipeline.objects.get(id=pipeline_id)

        if not pipeline.active:
            raise Pipeline.DoesNotExist

    except Pipeline.DoesNotExist:
        return RESPONSES["PIPELINE_NOT_ACTIVE"]

    if retry > 2:
        return RESPONSES["JOB_NOT_FOUND"]

    try:
        response = generate_signal(pipeline_id, header=header)
    except (ConnectionError, ReadTimeout):
        return RESPONSES["MODEL_APP_UNREACHABLE"]

    if "success" in response and response["success"]:
        return wait_for_job_conclusion(response["job_id"], pipeline_id, header=header, retry=retry)
    else:
        logging.info(response)
        return False, (response["message"] if "message" in response else response)


def wait_for_job_conclusion(job_id, pipeline_id, retry, header=''):

    # retries counts every poll, so the loop is guaranteed to terminate even
    # when responses are malformed or the job is stuck in an unknown state
    retries = 0
    while retries <= 10:

        try:
            response = check_job_status(job_id)
        except (ConnectionError, ReadTimeout):
            response = None

        if response and "status" in response:
            if response["code"] == "JOB_NOT_FOUND":
                return trigger_signal(pipeline_id, header=header, retry=retry+1)
            elif response["code"] == "FINISHED":
                logging.debug(header + f"Job {job_id} finished successfully.")

                if response["success"]:
                    return RESPONSES["SUCCESS"]
                else:
                    return RESPONSES["JOB_FAILED"]

            elif response["code"] == "FAILED":
                logging.debug(header + f"{job_id}: Job failed.")
                return RESPONSES["JOB_FAILED"]
            else:
                logging.debug(header + f"{job_id}: Waiting for job conclusion.")

        retries += 1
        time.sleep(5)

    return RESPONSES["TOO_MANY_RETRIES"]
