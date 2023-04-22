import logging
import os
from datetime import datetime, timedelta

import django
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline
from data.service.blueprints.bots_api import stop_instance


def check_app_is_running():
    """
    """
    logging.debug('Checking app status...')

    active_pipelines = Pipeline.objects.filter(active=True)

    for pipeline in active_pipelines:

        logging.debug(f'Checking pipeline {pipeline.id}...')

        if datetime.now(pytz.utc) - pipeline.last_entry > timedelta(minutes=10):

            logging.info(f'Pipeline {pipeline.id} found to be stuck. Sending stop request...')

            stop_instance(pipeline.id, '')
