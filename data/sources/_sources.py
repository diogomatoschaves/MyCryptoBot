import logging
import time

from data.service.external_requests import generate_signal, check_job_status
from shared.utils.exceptions import FailedSignalGeneration


# TODO: Implement logic to send this request
#  only if all data sources have updated the new row.
def trigger_signal(symbol, strategy, params, candle_size, exchange, retry=0):

    if retry > 2:
        raise FailedSignalGeneration(
            f"{symbol}: Maximum number of attempt to trigger new signal reached." +
            f"strategy: {strategy}, params: {params}, candle_size: {candle_size}, " +
            f"exchange: {exchange}"
        )

    response = generate_signal(symbol, strategy, params, candle_size, exchange)

    if "success" in response and response["success"]:
        return wait_for_job_conclusion(response["job_id"], symbol, strategy, params, candle_size, exchange, retry)
    else:
        logging.info(response["response"])
        return False


def wait_for_job_conclusion(job_id, symbol, strategy, params, candle_size, exchange, retry):

    retries = 0
    while True:

        response = check_job_status(job_id)

        if "status" in response:
            if response["status"] == "job not found":
                return generate_signal(symbol, strategy, params, candle_size, exchange, retry=retry+1)
            elif response["status"] == "finished":
                logging.debug(f"{symbol}: Job {job_id} finished successfully.")
                return True
            elif response["status"] in ["in-queue", "waiting"]:
                time.sleep(5)
            elif response["status"] == "failed":
                return False

            retries += 1

        if retries > 10:
            return False
