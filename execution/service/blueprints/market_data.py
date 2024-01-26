import os

import django
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from requests.exceptions import ConnectionError, ReadTimeout

from shared.exchanges import BinanceHandler
from shared.utils.decorators import retry_failed_connection
from shared.utils.exceptions import SymbolInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

market_data = Blueprint('market_data', __name__)

client = BinanceHandler()
testnet_client = BinanceHandler(paper_trading=True)


def get_ticker(symbol, paper_trading=False):
    try:
        client.validate_symbol(symbol)

        bh = testnet_client if paper_trading else client

        return bh.futures_symbol_ticker(symbol=symbol)
    except (SymbolInvalid, ConnectionError, ReadTimeout):
        return {}


def filter_balances(balances, coins):
    return [balance for balance in balances if balance['asset'] in coins]


def get_balances():
    testnet_balance = filter_balances(testnet_client.futures_account_balance(), ["USDT"])
    live_balance = filter_balances(client.futures_account_balance(), ["USDT"])

    return {"testnet": testnet_balance, "live": live_balance}


@market_data.get('/prices')
def get_current_price():

    symbol = request.args.get("symbol", None)

    return get_ticker(symbol)


@market_data.get('/futures_account_balance')
@retry_failed_connection(num_times=2)
@jwt_required()
def get_futures_account_balance():

    balances = get_balances()

    return jsonify(balances)


@market_data.get('/open-positions')
@retry_failed_connection(num_times=2)
@jwt_required()
def get_open_positions():

    symbol = request.args.get("symbol", None)

    test_positions = testnet_client.futures_position_information()
    live_positions = client.futures_position_information()

    test_position = None
    live_position = None

    for symbol_info in test_positions:
        if symbol_info["symbol"] == symbol:
            test_position = float(symbol_info["positionAmt"])

    for symbol_info in live_positions:
        if symbol_info["symbol"] == symbol:
            live_position = float(symbol_info["positionAmt"])

    open_positions = {
        "testnet": test_position,
        "live": live_position
    }

    success = test_position is not None and live_position is not None

    return jsonify({"positions": open_positions, "success": success})



