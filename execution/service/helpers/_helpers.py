import json
import os
from collections import namedtuple

import django
import redis

from execution.service.helpers.exceptions import SignalRequired, SignalInvalid
from shared.utils.config_parser import get_config
from shared.utils.helpers import get_pipeline_data, get_item_from_cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

config_vars = get_config('execution')

cache = redis.from_url(os.getenv('REDIS_URL', config_vars.redis_url))

fields = [
    "header",
    "binance_account_type",
    "initial_equity",
    "leverage",
]

Parameters = namedtuple(
    'Parameters',
    fields,
    defaults=(None,) * len(fields)
)


def validate_signal(signal):
    if signal is None:
        raise SignalRequired

    if signal not in [-1, 0, 1]:
        raise SignalInvalid(signal)


def get_header(pipeline_id):
    return json.loads(get_item_from_cache(cache, pipeline_id))


def extract_and_validate(request_data):

    binance_account_type = request_data.get('binance_account_type', 'futures')
    pipeline_id = request_data.get("pipeline_id", None)

    pipeline = get_pipeline_data(pipeline_id)

    header = get_header(pipeline_id)

    return pipeline, Parameters(header, binance_account_type, pipeline.initial_equity, pipeline.leverage)
