import os

import django
from django.core.paginator import Paginator
from flask import Blueprint, jsonify

from data.service.helpers import STRATEGIES
from shared.data.format_converter import ORDER_FORMAT_CONVERTER
from shared.exchanges.binance.constants import CANDLE_SIZES_MAPPER

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Exchange, Orders

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/resources/<resources>')
def get_resources(resources):

    resources = resources.split(',')

    response = {}

    for resource in resources:
        if resource == 'symbols':
            symbols = Symbol.objects.all().values()
            response["symbols"] = list(symbols)

        elif resource == 'exchanges':
            exchanges = Exchange.objects.all().values()
            response["exchanges"] = list(exchanges)

        elif resource == 'strategies':
            response["strategies"] = [{"name": key, **value} for key, value in STRATEGIES.items()]

        elif resource == 'candleSizes':
            response["candleSizes"] = [{"name": key} for key in CANDLE_SIZES_MAPPER.keys()]

    return jsonify(response)


@dashboard.route('/orders', defaults={'page': None})
@dashboard.route('/orders/<page>')
def get_orders(page):

    response = {}

    orders = Orders.objects.all().order_by('transact_time').values()

    paginator = Paginator(orders, 20)

    if page is None:
        page_obj = paginator.get_page(1)
        response["orders"] = list(page_obj)

    elif isinstance(page, int):
        page_obj = paginator.get_page(page)
        response["orders"] = list(page_obj)

    response["orders"] = [
        {ORDER_FORMAT_CONVERTER[key]: value for key, value in order.items() if key in ORDER_FORMAT_CONVERTER}
        for order in response["orders"]
    ]

    return jsonify(response)
