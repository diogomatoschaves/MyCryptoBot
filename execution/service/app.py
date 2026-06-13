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
from execution.service.reconciliation import reconcile_positions
from shared.utils.settings import settings
from shared.utils.decorators import handle_db_connection_error
from shared.utils.helpers import get_jwt_secret_key
from shared.utils.exceptions import EquityRequired
from shared.utils.logger import configure_logger
from shared.utils.events import publish_pipeline_event, EVENT_DEACTIVATED
from shared.utils.notifier import send_alert

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Position, Pipeline

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)


configure_logger(settings.logger_level)


global binance_futures_mock_trader, binance_futures_trader


def get_binance_trader_instance(paper_trading):
    if paper_trading:
        return binance_futures_mock_trader
    else:
        return binance_futures_trader


def startup_task():

    start_background_scheduler()

    # the exchange is the source of truth: repair any Position/Trade/units
    # drift left behind by a crash before trusting the local records below
    reconcile_positions(get_binance_trader_instance)

    # iterate pipelines (not Position rows) so pipelines without a Position
    # row are started - reconciliation creates the row when one is missing
    for pipeline in Pipeline.objects.filter(active=True):

        header = get_header(pipeline.id)

        try:
            start_pipeline_trade(pipeline, header)
        except InsufficientBalance:
            logging.info(f"Insufficient balance to start pipeline {pipeline.id}.")
            pipeline.active = False
            pipeline.save(update_fields=["active"])
            send_alert(
                title="Pipeline deactivated at startup",
                body=(
                    f"Pipeline {pipeline.id} ('{pipeline.name}'): insufficient balance "
                    f"to restart - deactivated; it will not trade until manually restarted."
                ),
                severity="critical",
                dedup_key=f"boot-failed-{pipeline.id}",
            )
            publish_pipeline_event(
                EVENT_DEACTIVATED, pipeline.id,
                reason="insufficient balance to restart at startup",
            )
        except Exception as e:
            # never let one bad pipeline crash app startup into a boot loop -
            # deactivate the offender and carry on with the rest
            logging.error(f"Failed to start pipeline {pipeline.id}: {e}")
            Pipeline.objects.filter(id=pipeline.id).update(active=False)
            send_alert(
                title="Pipeline deactivated at startup",
                body=(
                    f"Pipeline {pipeline.id} ('{pipeline.name}') failed to start "
                    f"({e}) - deactivated; it will not trade until manually restarted."
                ),
                severity="critical",
                dedup_key=f"boot-failed-{pipeline.id}",
            )
            publish_pipeline_event(
                EVENT_DEACTIVATED, pipeline.id,
                reason=f"failed to start at startup: {e}",
            )


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

    app.config["JWT_SECRET_KEY"] = get_jwt_secret_key()

    JWTManager(app)

    CORS(app, origins=os.getenv("CORS_ALLOWED_ORIGINS", "*").split(","))

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

        # falling through used to return None (jsonified to null), which
        # crashed callers that subscript the response
        return jsonify(Responses.EXCHANGE_INVALID(pipeline.exchange.name))

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

        return jsonify(Responses.EXCHANGE_INVALID(pipeline.exchange.name))

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
