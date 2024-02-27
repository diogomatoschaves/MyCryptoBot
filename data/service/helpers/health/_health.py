import time

from data.service.blueprints.bots_api import stop_instance


def stop_pipeline(pipeline_id, header='', raise_exception=False, nr_retries=2):

    success = False
    retries = 0

    while not success:
        if retries > nr_retries:
            break

        success = stop_instance(pipeline_id, header, raise_exception)

        retries += 1

        if not success:
            time.sleep(60)
