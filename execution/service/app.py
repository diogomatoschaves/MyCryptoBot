import logging
import os
import sys

from flask import Flask, jsonify, request

from execution.exchanges.binance import BinanceTrader
from shared.utils.logger import configure_logger

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

app_name = os.getenv("APP_NAME")

binance_trader = BinanceTrader()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "I'm up!"


@app.route('/start_symbol_trading', methods=['POST'])
def start_symbol_trading():
    request_data = request.get_json(force=True)

    logging.debug(request_data)

    symbol = request_data.get("symbol", None)
    exchange = request_data.get("exchange", 'binance')

    if exchange.lower() == 'binance':

        success = binance_trader.start_symbol_trading(symbol)

        if success:
            return jsonify({"success": success, "response": f"{symbol}: Trading symbol successfully started."})
        else:
            return jsonify({"success": success, "response": f"{symbol}: Trading symbol does not exist."})
    else:
        return jsonify({"response": f"Invalid {exchange} exchange.", "success": False})


@app.route('/stop_symbol_trading', methods=['POST'])
def stop_symbol_trading():
    request_data = request.get_json(force=True)

    logging.debug(request_data)

    symbol = request_data.get("symbol", None)
    exchange = request_data.get("exchange", 'binance')

    if exchange.lower() == 'binance':

        success = binance_trader.stop_symbol_trading(symbol)

        if success:
            return jsonify({"success": success, "response": f"{symbol}: Trading symbol successfully stopped."})
        else:
            return jsonify(
                {"success": success, "response": f"{symbol}: Trading symbol does not exist or was not being traded."}
            )
    else:
        return jsonify({"response": f"Invalid {exchange} exchange.", "success": False})


@app.route('/execute_order/<exchange>', methods=['POST'])
def execute_order(exchange):

    if exchange.lower() == 'binance':

        request_data = request.get_json(force=True)

        logging.debug(request_data)

        symbol = request_data.get("symbol", None)
        signal = request_data.get("signal", None)
        amount = request_data.get("amount", 'all')

        if symbol is None:
            return jsonify({"response": f"{symbol}: Invalid symbol.", "success": False})

        if signal is None:
            return jsonify({"response": f"{symbol}: Invalid {signal} signal.", "success": False})

        binance_trader.trade(symbol, signal, amount=amount)

        return jsonify({"response": f"{symbol}: Order was sent successfully.", "success": True})

    else:
        return jsonify({"response": f"Invalid {exchange} exchange.", "success": False})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
