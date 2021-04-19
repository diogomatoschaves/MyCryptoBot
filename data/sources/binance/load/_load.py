import os

from django.db import connection, transaction
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

unique_fields = {"open_time", "exchange", "symbol", "interval"}


def load_data(model_class, data, count_updates=True):

    if data.index.name == 'open_time':
        data = data.reset_index()

    new_entries = 0
    for index, row in data.iterrows():

        new_entry = save_new_entry_db(model_class, row, count_updates)

        new_entries += 1 if new_entry else 0

    return new_entries


def save_new_entry_db(model_class, fields, count_updates=True):

    new_entry = True
    try:
        with transaction.atomic():
            model_class.objects.create(**fields)
    except django.db.utils.IntegrityError as e:

        fields_subset = {key: value for key, value in fields.items() if key in unique_fields}

        rows = model_class.objects.filter(**fields_subset).update(**fields)

        if rows == 0 or not count_updates:
            new_entry = False

    return new_entry
