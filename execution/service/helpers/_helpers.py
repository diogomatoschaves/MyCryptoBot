import logging
import os

import django
from flask import jsonify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from execution.service.helpers.responses import Responses
from database.model.models import Symbol, Exchange
import shared.exchanges.binance.constants as const


def validate_input(**kwargs):

    print(kwargs)

    if "symbol" in kwargs:
        symbol = kwargs["symbol"]

        if symbol is None:
            return jsonify(Responses.SYMBOL_REQUIRED)

        try:
            Symbol.objects.get(name=symbol)
        except Symbol.DoesNotExist as e:
            logging.debug(symbol)
            logging.debug(e)
            return jsonify(Responses.SYMBOL_INVALID(symbol))

    if "exchange" in kwargs:
        exchange = kwargs["exchange"]

        if exchange is None:
            return jsonify(Responses.EXCHANGE_REQUIRED)

        try:
            Exchange.objects.get(name=exchange.lower())
        except (Exchange.DoesNotExist, AttributeError) as e:
            logging.debug(exchange)
            logging.debug(e)
            return jsonify(Responses.EXCHANGE_INVALID(exchange))

    if "signal" in kwargs:
        signal = kwargs["signal"]

        if signal is None:
            return jsonify(Responses.SIGNAL_REQUIRED)

        if signal not in [-1, 0, 1]:
            return jsonify(Responses.SIGNAL_INVALID(signal))

    return None
