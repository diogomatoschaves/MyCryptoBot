import os

import django
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from requests.exceptions import ConnectionError, ReadTimeout

from execution.service.helpers import extract_and_validate
from shared.exchanges.binance import BinanceHandler
from shared.utils.decorators import retry_failed_connection
from shared.utils.exceptions import SymbolInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

market_data = Blueprint('market_data', __name__)

client = BinanceHandler()
testnet_client = BinanceHandler(paper_trading=True)


@retry_failed_connection(num_times=2)
def get_ticker(symbol, paper_trading=False):
    try:
        client.validate_symbol(symbol)

        bh = testnet_client if paper_trading else client

        return bh.futures_symbol_ticker(symbol=symbol)
    except (SymbolInvalid, ConnectionError, ReadTimeout):
        return {}


def filter_balances(balances, coins):
    return [balance for balance in balances if balance['asset'] in coins]


@retry_failed_connection(num_times=2)
def get_balances():
    testnet_balance = filter_balances(testnet_client.futures_account_balance(), ["USDT"])
    live_balance = filter_balances(client.futures_account_balance(), ["USDT"])

    return {"testnet": testnet_balance, "live": live_balance}


@retry_failed_connection(num_times=2)
def get_account_data():
    testnet_balance = testnet_client.futures_account()
    live_balance = client.futures_account()

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


def process_positions(positions, open_positions):
    for symbol_info in positions:
        units = float(symbol_info["positionAmt"])
        if units != 0:
            open_positions.append({
                "symbol": symbol_info["symbol"],
                "units": units
            })

    return open_positions


@market_data.get('/open-positions')
@retry_failed_connection(num_times=2)
@jwt_required()
def get_open_positions():

    test_positions = testnet_client.futures_position_information()
    live_positions = client.futures_position_information()

    open_positions = {
        "testnet": process_positions(test_positions, []),
        "live": process_positions(live_positions, [])
    }

    return jsonify({"positions": open_positions, "success": True})
