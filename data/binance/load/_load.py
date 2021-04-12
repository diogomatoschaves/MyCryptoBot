import logging
import os

import pytz
from django.db import connection
import django
import pandas as pd


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Asset, Symbol, Exchange


def get_symbol(quote, base):

    symbol = base + quote

    try:
        return Symbol.objects.get(name=symbol)
    except:
        quote_asset = Asset.objects.get_or_create(symbol=quote)[0]
        base_asset = Asset.objects.get_or_create(symbol=base)[0]

        obj = Symbol(name=symbol, quote=quote_asset, base=base_asset)
        obj.save()

        return obj


def save_new_entry_db(model_class, row, quote, base, exchange, interval):

    fields = {}
    fields.update(row)

    fields.update({
        "exchange": Exchange.objects.get_or_create(name=exchange)[0],
        "symbol": get_symbol(quote, base),
        "interval": interval
    })

    new_entry = True
    try:
        model_class.objects.create(**fields)
    except django.db.utils.IntegrityError as e:

        new_entry = False

        unique_fields = {"open_time", "exchange", "symbol", "interval"}

        fields_subset = {key: value for key, value in fields.items() if key in unique_fields}

        model_class.objects.filter(**fields_subset).update(**fields)

    return new_entry
