import json
import os
from collections import namedtuple

import django
import redis

from execution.service.helpers.exceptions import NoSuchPipeline, PipelineNotActive, SignalRequired, SignalInvalid
from shared.utils.helpers import get_pipeline_data, get_item_from_cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


fields = [
    "response",
    "header",
    "binance_account_type",
    "equity"
]

Parameters = namedtuple(
    'Parameters',
    fields,
    defaults=(None,) * len(fields)
)


cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


def validate_input(**kwargs):

    if "signal" in kwargs:
        signal = kwargs["signal"]

        if signal is None:
            raise SignalRequired

        if signal not in [-1, 0, 1]:
            raise SignalInvalid(signal)

    return None


def extract_and_validate(request_data):

    binance_account_type = request_data.get('binance_account_type', 'futures')
    equity = request_data.get('equity', None)
    pipeline_id = request_data.get("pipeline_id", None)

    pipeline_exists, pipeline = get_pipeline_data(pipeline_id)

    if pipeline_exists:
        if not pipeline.active:
            raise PipelineNotActive(pipeline_id)
    else:
        raise NoSuchPipeline(pipeline_id)

    header = json.loads(get_item_from_cache(cache, pipeline_id))

    return pipeline, Parameters(None, header, binance_account_type, equity)
