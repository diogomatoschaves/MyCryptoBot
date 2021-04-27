import logging
import os
import sys

from flask import Flask, jsonify, request

from execution.exchanges.binance import BinanceTrader
from execution.service.helpers import validate_input
from execution.service.helpers.responses import Responses
from shared.utils.logger import configure_logger

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

binance_trader = BinanceTrader()


app = Flask(__name__)


def extract_and_validate():
    request_data = request.get_json(force=True)

    logging.debug(request_data)

    symbol = request_data.get("symbol", None)
    exchange = request_data.get("exchange", None)

    response = validate_input(
        symbol=symbol,
        exchange=exchange
    )

    return symbol, exchange, response


@app.route('/')
def hello_world():
    return "I'm up!"


@app.route('/start_symbol_trading', methods=['POST'])
def start_symbol_trading():

    symbol, exchange, response = extract_and_validate()

    if response is not None:
        logging.debug(response)
        return response

    if exchange.lower() == 'binance':

        success = binance_trader.start_symbol_trading(symbol)

        if success:
            return jsonify(Responses.TRADING_SYMBOL_START(success, symbol))
        else:
            return jsonify(Responses.TRADING_SYMBOL_NO_ACCOUNT(symbol))
    else:
        return jsonify(Responses.EXCHANGE_INVALID(exchange))


@app.route('/stop_symbol_trading', methods=['POST'])
def stop_symbol_trading():
    symbol, exchange, response = extract_and_validate()

    if response is not None:
        logging.debug(response)
        return response

    if exchange.lower() == 'binance':

        success = binance_trader.stop_symbol_trading(symbol)

        if success:
            return jsonify(Responses.TRADING_SYMBOL_STOP(success, symbol))
        else:
            return jsonify(Responses.TRADING_SYMBOL_NOT_ACTIVE(symbol))
    else:
        return jsonify(Responses.EXCHANGE_INVALID(exchange))


@app.route('/execute_order/<exchange>', methods=['POST'])
def execute_order(exchange):

    request_data = request.get_json(force=True)

    logging.debug(request_data)

    symbol = request_data.get("symbol", None)
    signal = request_data.get("signal", None)
    amount = "all"

    response = validate_input(
        symbol=symbol,
        signal=signal,
        exchange=exchange
    )

    if response is not None:
        logging.debug(response)
        return response

    if exchange.lower() == 'binance':

        binance_trader.trade(symbol, signal, amount=amount)

        return jsonify(Responses.ORDER_EXECUTION_SUCCESS(symbol))

    else:
        return jsonify(Responses.EXCHANGE_INVALID(exchange))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
