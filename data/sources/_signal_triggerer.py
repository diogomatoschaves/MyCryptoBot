import logging
import os
import time

from data.service.external_requests import generate_signal, check_job_status


# TODO: Implement logic to send this request
#  only if all data sources have updated the new row.
def trigger_signal(pipeline_id, header='', retry=0):

    if retry > 2:
        return False

    response = generate_signal(pipeline_id, header=header)

    if "success" in response and response["success"]:
        return wait_for_job_conclusion(response["job_id"], pipeline_id, header=header, retry=retry)
    else:
        logging.info(response["message"])
        return False


def wait_for_job_conclusion(job_id, pipeline_id, retry, header=''):

    retries = 0
    while True:

        response = check_job_status(job_id)

        if "status" in response:
            if response["code"] == "JOB_NOT_FOUND":
                return trigger_signal(pipeline_id, header=header, retry=retry+1)
            elif response["code"] == "FINISHED":
                logging.debug(header + f"Job {job_id} finished successfully.")
                return True
            elif response["code"] in ["IN_QUEUE", "WAITING"]:
                logging.debug(header + f"{job_id}: Waiting for job conclusion.")
            elif response["code"] == "FAILED":
                return False

        if retries > 4:
            return False

        time.sleep(4)
