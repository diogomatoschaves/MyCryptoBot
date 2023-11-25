import logging
import os
from datetime import datetime

import pytz
from django.db import connection, transaction
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline

unique_fields = {"open_time", "exchange", "symbol", "interval"}


def load_data(model_class, data, pipeline_id, update_duplicate=True, header=''):

    logging.debug(f'Saving data with {data.shape[0]} rows and {data.shape[1]} columns.')

    if data.index.name == 'open_time':
        data = data.reset_index()

    new_entries = 0
    for index, row in data.iterrows():

        new_entry = save_new_entry_db(model_class, row, update_duplicate)

        new_entries += 1 if new_entry else 0

    Pipeline.objects.filter(id=pipeline_id).update(last_entry=datetime.now(pytz.utc))

    return new_entries


def save_new_entry_db(model_class, fields, count_updates=True):

    new_entry = True
    try:
        with transaction.atomic():
            model_class.objects.create(**fields)
    except ValueError as e:
        logging.debug(e)
        logging.debug(fields)

        fields["close_time"] = None
        with transaction.atomic():
            model_class.objects.create(**fields)
    except django.db.utils.IntegrityError as e:
        logging.debug(e)
        logging.debug(fields)

        new_entry = False
        if count_updates:

            fields_subset = {key: value for key, value in fields.items() if key in unique_fields}

            rows = model_class.objects.filter(**fields_subset).update(**fields)

            if rows != 0 and count_updates:
                new_entry = True

    return new_entry
