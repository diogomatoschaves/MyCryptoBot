import logging
import os
from collections import defaultdict
from datetime import datetime

import pandas as pd
import pytz
from django.db import transaction
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline

UNIQUE_FIELDS = ("open_time", "exchange_id", "symbol_id", "interval")


def load_data(model_class, data, pipeline_id, update_duplicate=True, header=''):

    logging.debug(f'Saving data with {data.shape[0]} rows and {data.shape[1]} columns.')

    if data.index.name == 'open_time':
        data = data.reset_index()

    records = [_clean_record(record) for record in data.to_dict('records')]

    try:
        new_entries = _bulk_load(model_class, records, update_duplicate)
    except (ValueError, TypeError) as e:
        # a row that can't be bulk-adapted falls back to the resilient,
        # one-row-at-a-time path rather than failing the whole batch
        logging.warning(f'Bulk load failed ({e}); falling back to row-by-row.')
        new_entries = sum(
            1 if save_new_entry_db(model_class, record, update_duplicate) else 0
            for record in records
        )

    Pipeline.objects.filter(id=pipeline_id).update(last_entry=datetime.now(pytz.utc))

    return new_entries


def _clean_record(record):
    # pandas leaves NaN/NaT in absent cells; Django wants None
    return {key: (None if pd.isna(value) else value) for key, value in record.items()}


def _entry_key(record):
    return tuple(record.get(field) for field in UNIQUE_FIELDS)


def _bulk_load(model_class, records, update_duplicate):
    """Insert candle rows in bulk, splitting new rows from duplicates in a
    single existence query. Returns the number of rows counted as written
    (new rows always; duplicates only when update_duplicate is True).
    """
    if not records:
        return 0

    open_times = [record["open_time"] for record in records]

    existing_keys = set(
        model_class.objects
        .filter(open_time__in=open_times)
        .values_list(*UNIQUE_FIELDS)
    )

    new_records, duplicate_records = [], []
    for record in records:
        target = duplicate_records if _entry_key(record) in existing_keys else new_records
        target.append(record)

    with transaction.atomic():
        to_insert = list(new_records)

        if update_duplicate and duplicate_records:
            # delete the existing rows being replaced, grouped by their
            # (exchange, symbol, interval) so the open_time filter stays scoped
            groups = defaultdict(list)
            for record in duplicate_records:
                groups[
                    (record.get("exchange_id"), record.get("symbol_id"), record.get("interval"))
                ].append(record["open_time"])

            for (exchange_id, symbol_id, interval), times in groups.items():
                model_class.objects.filter(
                    exchange_id=exchange_id,
                    symbol_id=symbol_id,
                    interval=interval,
                    open_time__in=times,
                ).delete()

            to_insert += duplicate_records

        model_class.objects.bulk_create(
            [model_class(**record) for record in to_insert],
            ignore_conflicts=True,
        )

    return len(new_records) + (len(duplicate_records) if update_duplicate else 0)


def save_new_entry_db(model_class, fields, count_updates=True):
    """Resilient single-row insert used as the fallback when a batch can't be
    bulk-loaded. Returns True when the row counts as written.
    """
    fields = _clean_record(dict(fields))

    try:
        with transaction.atomic():
            model_class.objects.create(**fields)
        return True
    except ValueError as e:
        logging.debug(e)
        fields["close_time"] = None
        with transaction.atomic():
            model_class.objects.create(**fields)
        return True
    except django.db.utils.IntegrityError as e:
        logging.debug(e)

        if not count_updates:
            return False

        fields_subset = {key: value for key, value in fields.items() if key in UNIQUE_FIELDS}
        with transaction.atomic():
            model_class.objects.filter(**fields_subset).delete()
            model_class.objects.create(**fields)
        return True
