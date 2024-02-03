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
from execution.service.helpers.exceptions import PipelineNotActive
from execution.service.helpers.responses import Responses
from execution.exchanges.binance.futures import BinanceFuturesTrader
from shared.utils.config_parser import get_config
from shared.utils.decorators import handle_db_connection_error
from shared.utils.exceptions import EquityRequired
from shared.utils.helpers import get_pipeline_data
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

    open_positions = Position.objects.filter(pipeline__active=True)

    for open_position in open_positions:

        pipeline = get_pipeline_data(open_position.pipeline_id)

        header = get_header(pipeline.id)

        start_pipeline_trade(pipeline, header, initial_position=open_position.position)


def start_pipeline_trade(pipeline, header, initial_position=0):

    bt = get_binance_trader_instance(pipeline.paper_trading)

    bt.start_symbol_trading(
        pipeline.symbol,
        pipeline.current_equity,
        pipeline.id,
        leverage=pipeline.leverage,
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
    jwt = JWTManager(app)

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

        if parameters.initial_equity is None:
            raise EquityRequired

        if pipeline.exchange == 'binance':

            start_pipeline_trade(pipeline, parameters.header)

            return jsonify(Responses.TRADING_SYMBOL_START(pipeline.symbol))

    @app.route('/stop_symbol_trading', methods=['POST'])
    @handle_app_errors
    @binance_error_handler(request_obj=request)
    @jwt_required()
    @handle_db_connection_error
    def stop_symbol_trading():

        request_data = request.get_json(force=True)

        pipeline, parameters = extract_and_validate(request_data)

        bt = get_binance_trader_instance(pipeline.paper_trading)

        if not pipeline.active:
            bt.stop_symbol_trading(pipeline.symbol, header=parameters.header, pipeline_id=pipeline.id)
            raise PipelineNotActive(pipeline.id)

        bt.stop_symbol_trading(pipeline.symbol, header=parameters.header, pipeline_id=pipeline.id)

        return jsonify(Responses.TRADING_SYMBOL_STOP(pipeline.symbol))

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

        signal = request_data.get("signal", None)
        amount = request_data.get("amount", "all")

        validate_signal(signal=signal)

        if pipeline.exchange.lower() == 'binance':

            bt = get_binance_trader_instance(pipeline.paper_trading)

            return_value = handle_order_execution_errors(
                symbol=pipeline.symbol,
                trader_instance=bt,
                header=parameters.header,
                pipeline_id=pipeline.id
            )(
                lambda: bt.trade(pipeline.symbol, signal, amount=amount, header=parameters.header, pipeline_id=pipeline.id)
            )()

            if return_value:
                return jsonify(return_value)

        return jsonify(Responses.ORDER_EXECUTION_SUCCESS(pipeline.symbol))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0')
