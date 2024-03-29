import logging
import os
import sys

import django
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required

from execution.service.cron_jobs.main import start_background_scheduler
from execution.service.helpers.decorators import binance_error_handler, handle_app_errors, handle_order_execution_errors
from execution.service.blueprints.market_data import market_data
from execution.service.helpers import validate_signal, extract_and_validate, get_header
from execution.service.helpers.exceptions import PipelineNotActive, InsufficientBalance
from execution.service.helpers.responses import Responses
from execution.exchanges.binance.futures import BinanceFuturesTrader
from shared.utils.config_parser import get_config
from shared.utils.decorators import handle_db_connection_error
from shared.utils.exceptions import EquityRequired
from shared.utils.logger import configure_logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Position

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

config_vars = get_config('execution')

configure_logger(os.getenv("LOGGER_LEVEL", config_vars.logger_level))


global binance_futures_mock_trader, binance_futures_trader


def get_binance_trader_instance(paper_trading):
    if paper_trading:
        return binance_futures_mock_trader
    else:
        return binance_futures_trader


def startup_task():

    start_background_scheduler(config_vars)

    active_pipelines = [position.pipeline for position in Position.objects.filter(pipeline__active=True)]

    for pipeline in active_pipelines:

        header = get_header(pipeline.id)

        try:
            start_pipeline_trade(pipeline, header)
        except InsufficientBalance:
            logging.info(f"Insufficient balance to start pipeline {pipeline.id}.")
            pipeline.active = False
            pipeline.save()


def start_pipeline_trade(pipeline, header):
    try:
        initial_position = Position.objects.get(pipeline__id=pipeline.id).position
    except Position.DoesNotExist:
        initial_position = 0

    bt = get_binance_trader_instance(pipeline.paper_trading)

    bt.start_symbol_trading(
        pipeline.id,
        initial_position=initial_position,
        header=header,
    )


def create_app():

    global binance_futures_mock_trader, binance_futures_trader

    binance_futures_trader = BinanceFuturesTrader()
    binance_futures_mock_trader = BinanceFuturesTrader(paper_trading=True)

    app = Flask(__name__)
    app.register_blueprint(market_data)

    app.config["JWT_SECRET_KEY"] = os.getenv('SECRET_KEY')

    JWTManager(app)

    CORS(app)

    startup_task()

    @app.route('/')
    @jwt_required()
    def hello_world():
        return "I'm up!"

    @app.route('/start_symbol_trading', methods=['POST'])
    @handle_app_errors
    @binance_error_handler(request_obj=request)
    @jwt_required()
    @handle_db_connection_error
    def start_symbol_trading():

        request_data = request.get_json(force=True)

        pipeline, parameters = extract_and_validate(request_data)

        if pipeline.initial_equity is None:
            raise EquityRequired

        if pipeline.exchange.name == 'binance':
            start_pipeline_trade(pipeline, parameters.header)

            return jsonify(Responses.TRADING_SYMBOL_START(pipeline.symbol.name))

    @app.route('/stop_symbol_trading', methods=['POST'])
    @handle_app_errors
    @binance_error_handler(request_obj=request)
    @jwt_required()
    @handle_db_connection_error
    def stop_symbol_trading():

        request_data = request.get_json(force=True)

        pipeline, parameters = extract_and_validate(request_data)

        if not parameters.force and not pipeline.active:
            raise PipelineNotActive(pipeline.id)

        if parameters.force or pipeline.exchange.name == 'binance':

            paper_trading = pipeline.paper_trading if pipeline is not None else parameters.paper_trading
            symbol = pipeline.symbol.name if pipeline is not None else parameters.symbol
            pipeline_id = pipeline.id if pipeline is not None else None

            bt = get_binance_trader_instance(paper_trading)

            bt.stop_symbol_trading(pipeline_id, symbol, header=parameters.header, force=parameters.force)

            return jsonify(Responses.TRADING_SYMBOL_STOP(symbol))

    @app.route('/execute_order', methods=['POST'])
    @handle_app_errors
    @jwt_required()
    @handle_db_connection_error
    def execute_order():

        request_data = request.get_json(force=True)

        logging.debug(request_data)

        pipeline, parameters = extract_and_validate(request_data)

        if not pipeline.active:
            raise PipelineNotActive(pipeline.id)

        validate_signal(signal=parameters.signal)

        if pipeline.exchange.name.lower() == 'binance':

            bt = get_binance_trader_instance(pipeline.paper_trading)

            return_value = handle_order_execution_errors(
                symbol=pipeline.symbol.name,
                trader_instance=bt,
                header=parameters.header,
                pipeline_id=pipeline.id
            )(
                lambda: bt.trade(
                    pipeline.symbol.name,
                    parameters.signal,
                    amount=parameters.amount,
                    header=parameters.header,
                    pipeline_id=pipeline.id,
                    print_results=True
                )
            )()

            if return_value:
                return jsonify(return_value)

        return jsonify(Responses.ORDER_EXECUTION_SUCCESS(pipeline.symbol.name))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0')
