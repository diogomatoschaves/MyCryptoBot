import logging
import os
from datetime import datetime, timedelta

import django
import pytz

from data.service.helpers.health import stop_pipeline
from shared.utils.decorators import handle_db_connection_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline


@handle_db_connection_error
def check_app_is_running():
    """
    """
    logging.info('Checking app status...')

    active_pipelines = Pipeline.objects.filter(active=True)

    for pipeline in active_pipelines:

        logging.debug(f'Checking pipeline {pipeline.id}...')

        now = datetime.now(pytz.utc)

        if pipeline.last_entry and now - pipeline.last_entry > timedelta(minutes=10):

            logging.info(f'Pipeline {pipeline.id} found to be stuck. Sending stop request...')

            stop_pipeline(pipeline.id, '', raise_exception=False)
