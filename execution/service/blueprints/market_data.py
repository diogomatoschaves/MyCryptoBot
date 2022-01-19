import os

import django
from flask import Blueprint, request

from shared.exchanges import BinanceHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol

market_data = Blueprint('market_data', __name__)

client = BinanceHandler()


@market_data.route('/prices/', methods=['GET'])
def get_current_price():

    request_data = request.get_json(force=True)

    symbol = request_data.get("symbol", None)

    if Symbol.objects.filter(symbol_id=symbol).exists:

        return client.get_symbol_ticker(symbol=symbol)

    else:
        return {}
