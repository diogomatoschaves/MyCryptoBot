import os

import django
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from shared.exchanges import BinanceHandler
from shared.utils.decorators import retry_failed_connection
from shared.utils.exceptions import SymbolInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

market_data = Blueprint('market_data', __name__)

client = BinanceHandler()
testnet_client = BinanceHandler(paper_trading=True)


@market_data.route('/prices', methods=['GET'])
def get_current_price():

    symbol = request.args.get("symbol", None)

    try:
        client.validate_symbol(symbol)
        return client.futures_symbol_ticker(symbol=symbol)
    except SymbolInvalid:
        return {}


@market_data.route('/futures_account_balance', methods=['GET'])
@retry_failed_connection(num_times=2)
@jwt_required()
def get_futures_account_balance():

    balances = {"testnet": testnet_client.futures_account_balance(), "live": client.futures_account_balance()}

    return jsonify(balances)



