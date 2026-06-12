import json
import logging
import os

import django
import redis
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from data.service.blueprints.bots_api._helpers import start_symbol_trading, stop_instance
from data.service.external_requests import get_strategies, start_stop_symbol_trading
from data.service.helpers import check_input, get_or_create_pipeline, extract_request_params, convert_client_request
from shared.utils.config_parser import get_config
from shared.utils.decorators import general_app_error
from data.service.helpers.decorators.handle_app_errors import handle_app_errors
from data.service.helpers.exceptions import (
    PipelineStartFail, DataPipelineDoesNotExist, DataPipelineCouldNotBeStopped,
)
from data.service.helpers.responses import Responses
from shared.utils.decorators import handle_db_connection_error
from shared.utils.helpers import get_item_from_cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline

config_vars = get_config()

cache = redis.from_url(os.getenv('REDIS_URL', config_vars.redis_url))

bots_api = Blueprint('bots_api', __name__)


@bots_api.put('/start_bot')
@general_app_error
@handle_app_errors
@jwt_required()
@handle_db_connection_error
def start_bot():

    # cache strategies, but never cache a failed fetch (None) - otherwise a
    # transient model-app outage poisons the cache for the process lifetime
    STRATEGIES = globals().get("STRATEGIES")
    if not STRATEGIES:
        STRATEGIES = get_strategies()
        if STRATEGIES:
            globals()["STRATEGIES"] = STRATEGIES

    request_data = extract_request_params(request)

    exists = check_input(STRATEGIES, **request_data)

    data = convert_client_request(request_data)

    pipeline = get_or_create_pipeline(
        exists,
        request_data["pipeline_id"],
        request_data["strategy"],
        data
    )

    response = start_symbol_trading(pipeline)

    if not response["success"]:
        raise PipelineStartFail(pipeline.id)

    return jsonify(Responses.DATA_PIPELINE_START_OK(pipeline))


@bots_api.put('/stop_bot')
@general_app_error
@handle_app_errors()
@jwt_required()
@handle_db_connection_error
def stop_bot():

    # Stops the data collection stream
    # closes any open positions

    data = request.get_json(force=True)

    pipeline_id = data.get("pipelineId", None)

    try:
        header = json.loads(get_item_from_cache(cache, pipeline_id))

        logging.info(header + f"Stopping pipeline {pipeline_id}.")

        stopped = stop_instance(pipeline_id, header=header, raise_exception=True)

        pipeline = Pipeline.objects.get(id=pipeline_id)

        if not stopped:
            # no local data instance is attached (e.g. after a worker restart),
            # so the exchange position was never closed - tell the execution
            # service directly to force-close it before deactivating
            logging.info(header + f"No local instance for pipeline {pipeline_id}; forcing stop.")
            response = start_stop_symbol_trading(
                {
                    "paper_trading": pipeline.paper_trading,
                    "symbol": pipeline.symbol.name,
                    "force": True,
                },
                'stop',
            )
            if not response["success"]:
                raise DataPipelineCouldNotBeStopped(response["message"])

        pipeline.active = False
        pipeline.save(update_fields=["active"])

        return jsonify(Responses.DATA_PIPELINE_STOPPED(pipeline))
    except Pipeline.DoesNotExist:
        raise DataPipelineDoesNotExist(pipeline_id)
