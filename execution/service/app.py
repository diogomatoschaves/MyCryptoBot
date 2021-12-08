import logging
import os
import sys

from flask import Flask, jsonify, request

from execution.exchanges.binance import BinanceTrader
from execution.service.helpers import validate_input, extract_and_validate
from execution.service.helpers.responses import Responses
from shared.utils.logger import configure_logger

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

binance_trader = BinanceTrader()


app = Flask(__name__)


@app.route('/')
def hello_world():
    return "I'm up!"


@app.route('/start_symbol_trading', methods=['POST'])
def start_symbol_trading():

    pipeline, response = extract_and_validate()

    if response is not None:
        logging.debug(response)
        return response

    if pipeline.exchange.lower() == 'binance':

        success = binance_trader.start_symbol_trading(pipeline.symbol)

        if success:
            return jsonify(Responses.TRADING_SYMBOL_START(pipeline.symbol))
        else:
            return jsonify(Responses.TRADING_SYMBOL_NO_ACCOUNT(pipeline.symbol))


@app.route('/stop_symbol_trading', methods=['POST'])
def stop_symbol_trading():
    pipeline, response = extract_and_validate()

    if response is not None:
        logging.debug(response)
        return response

    if pipeline.exchange.lower() == 'binance':

        success = binance_trader.stop_symbol_trading(pipeline.symbol)

        if success:
            return jsonify(Responses.TRADING_SYMBOL_STOP(pipeline.symbol))
        else:
            return jsonify(Responses.TRADING_SYMBOL_NO_ACCOUNT(pipeline.symbol))


@app.route('/execute_order', methods=['POST'])
def execute_order():

    request_data = request.get_json(force=True)

    logging.debug(request_data)

    pipeline, response = extract_and_validate()

    if response is not None:
        logging.debug(response)
        return response

    signal = request_data.get("signal", None)
    amount = request_data.get("amount", "all")

    response = validate_input(signal=signal)

    if response is not None:
        logging.debug(response)
        return response

    if pipeline.exchange.lower() == 'binance':

        binance_trader.trade(pipeline.symbol, signal, amount=amount)

        return jsonify(Responses.ORDER_EXECUTION_SUCCESS(pipeline.symbol))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
