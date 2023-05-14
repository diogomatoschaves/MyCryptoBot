import os

import django
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from data.service.external_requests import get_price, get_balance
from shared.utils.decorators import general_app_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


proxy = Blueprint('proxy', __name__)


@proxy.get('/prices')
@general_app_error
@jwt_required()
def get_current_price():

    symbol = request.args.get("symbol", None)

    return get_price(symbol)


@proxy.get('/futures_account_balance')
@general_app_error
@jwt_required()
def get_futures_account_balance():
    return get_balance()
