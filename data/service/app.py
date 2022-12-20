import functools
import json
import os
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from functools import reduce

from flask import Flask, jsonify, request
import django
from flask_cors import CORS

import redis
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from data.service.blueprints.user_management import user_management
from data.service.blueprints.dashboard import dashboard
from data.service.external_requests import start_stop_symbol_trading, get_strategies
from data.service.helpers.decorators.handle_app_errors import handle_app_errors
from data.service.helpers.exceptions import PipelineStartFail
from data.service.helpers.exceptions.data_pipeline_does_not_exist import DataPipelineDoesNotExist
from data.service.helpers.responses import Responses
from data.sources._sources import DataHandler
from shared.exchanges import BinanceHandler
from shared.utils.decorators import handle_db_connection_error
from shared.utils.helpers import get_logging_row_header, get_item_from_cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from data.service.helpers import check_input, get_or_create_pipeline
from database.model.models import Pipeline, Position
from shared.utils.logger import configure_logger

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

executor = ThreadPoolExecutor(16)


binance_instances = []

binance_client = BinanceHandler()

cache = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))


def initialize_data_collection(pipeline, header):

    data_handler = DataHandler(pipeline, header=header)

    global binance_instances
    binance_instances.append(data_handler.binance_handler)


def reduce_instances(instances, instance, pipeline_id, header):
    if pipeline_id == instance.pipeline_id:
        instance.stop_data_ingestion(header=header)
        return instances
    else:
        return [*instances, instance]


def stop_instance(pipeline_id, header):

    global binance_instances

    binance_instances = reduce(
        lambda instances, instance: reduce_instances(instances, instance, pipeline_id, header),
        binance_instances,
        []
    )


def startup_task(app):

    open_positions = Position.objects.filter(open=True)

    with app.app_context():
        access_token = create_access_token(identity='abc', expires_delta=False)
        bearer_token = 'Bearer ' + access_token
        cache.set("bearer_token", bearer_token)

    for open_position in open_positions:

        start_symbol_trading(open_position.pipeline)
        open_position.pipeline.active = True
        open_position.pipeline.save()


def start_symbol_trading(pipeline):

    header = get_logging_row_header(pipeline)

    cache.set(
        f"pipeline {pipeline.id}",
        json.dumps(header)
    )

    logging.info(header + f"Starting data pipeline.")

    executor.submit(
        initialize_data_collection,
        pipeline,
        header
    )


def create_app():
    app = Flask(__name__)
    app.debug = False
    app.register_blueprint(dashboard)
    app.register_blueprint(user_management)

    app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=3)

    jwt = JWTManager(app)

    CORS(app)

    startup_task(app)

    @app.route('/')
    @jwt_required()
    def hello_world():
        return "I'm up!"

    @app.route('/start_bot', methods=['PUT'])
    @handle_app_errors
    @jwt_required()
    @handle_db_connection_error
    def start_bot():

        if "STRATEGIES" not in globals():
            STRATEGIES = get_strategies()
            globals()["STRATEGIES"] = STRATEGIES
        else:
            STRATEGIES = globals()["STRATEGIES"]

        data = request.get_json(force=True)

        name = data.get("name", None)
        color = data.get("color", None)
        allocation = data.get("allocation", None)
        symbol = data.get("symbol", None)
        strategy = data.get("strategy", None)
        params = data.get("params", {})
        candle_size = data.get("candleSize", None)
        exchange = data.get("exchanges", None)
        paper_trading = data.get("paperTrading") if type(data.get("paperTrading")) == bool else False
        leverage = data.get("leverage", 1)

        check_input(
            binance_client,
            STRATEGIES,
            name=name,
            color=color,
            allocation=allocation,
            symbol=symbol,
            strategy=strategy,
            params=params,
            candle_size=candle_size,
            exchange=exchange,
            leverage=leverage
        )

        exchange = exchange.lower()
        candle_size = candle_size.lower()

        pipeline = get_or_create_pipeline(
            name=name,
            color=color,
            allocation=allocation,
            symbol=symbol,
            candle_size=candle_size,
            strategy=strategy,
            exchange=exchange,
            params=params,
            paper_trading=paper_trading,
            leverage=leverage
        )

        payload = {
            "pipeline_id": pipeline.id,
            "binance_trader_type": "futures",
        }

        response = start_stop_symbol_trading(payload, 'start')

        if not response["success"]:
            logging.warning(response["message"])

            pipeline.active = False
            pipeline.save()

            raise PipelineStartFail(response)

        start_symbol_trading(pipeline)

        return jsonify(Responses.DATA_PIPELINE_START_OK(pipeline))

    @app.put('/stop_bot')
    @handle_app_errors()
    @jwt_required()
    @handle_db_connection_error
    def stop_bot():

        # Stops the data collection stream
        # closes any open positions

        data = request.get_json(force=True)

        pipeline_id = data.get("pipelineId", None)

        try:
            pipeline = Pipeline.objects.get(id=pipeline_id)

            header = json.loads(get_item_from_cache(cache, pipeline_id))

            logging.info(header + f"Stopping data pipeline.")

            stop_instance(pipeline_id, header=header)

            response = start_stop_symbol_trading({"pipeline_id": pipeline.id}, 'stop')

            logging.debug(response["message"])

            pipeline.active = False
            pipeline.open_time = None
            pipeline.save()

            return jsonify(Responses.DATA_PIPELINE_STOPPED(pipeline))
        except Pipeline.DoesNotExist:
            raise DataPipelineDoesNotExist(pipeline_id)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0')
