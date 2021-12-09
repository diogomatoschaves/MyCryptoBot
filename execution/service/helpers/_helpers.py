import json
import logging
import os

import django
import redis
from flask import jsonify, request

from shared.utils.helpers import get_pipeline_data, get_item_from_cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from execution.service.helpers.responses import Responses


cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))


def validate_input(**kwargs):

    if "signal" in kwargs:
        signal = kwargs["signal"]

        if signal is None:
            return jsonify(Responses.SIGNAL_REQUIRED)

        if signal not in [-1, 0, 1]:
            return jsonify(Responses.SIGNAL_INVALID(signal))

    return None


def extract_and_validate():
    request_data = request.get_json(force=True)

    logging.debug(request_data)

    pipeline_id = request_data.get("pipeline_id", None)

    pipeline_exists, pipeline = get_pipeline_data(pipeline_id)

    if pipeline_exists:
        if not pipeline.active:
            return pipeline, jsonify(Responses.PIPELINE_NOT_ACTIVE(pipeline.symbol, pipeline_id)), None
    else:
        return pipeline, jsonify(Responses.NO_SUCH_PIPELINE(pipeline_id)), None

    header = json.loads(get_item_from_cache(cache, pipeline_id))

    return pipeline, None, header
