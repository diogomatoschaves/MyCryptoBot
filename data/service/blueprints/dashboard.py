import os

import django
from django.core.paginator import Paginator
from flask import Blueprint, jsonify

from data.service.external_requests import get_strategies
from data.service.helpers._helpers import convert_queryset_to_dict
from shared.data.format_converter import TRADE_FORMAT_CONVERTER, PIPELINE_FORMAT_CONVERTER, POSITION_FORMAT_CONVERTER
from shared.exchanges.binance.constants import CANDLE_SIZES_MAPPER

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Exchange, Orders, Pipeline, Position, Trade

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/resources/<resources>')
def get_resources(resources):

    resources = resources.split(',')

    response = {}

    for resource in resources:
        if resource == 'symbols':
            symbols = Symbol.objects.all().values()
            response["symbols"] = convert_queryset_to_dict(symbols)

        elif resource == 'exchanges':
            exchanges = Exchange.objects.all().values()
            response["exchanges"] = convert_queryset_to_dict(exchanges)

        elif resource == 'strategies':
            strategies = get_strategies()
            response["strategies"] = strategies

        elif resource == 'candleSizes':
            response["candleSizes"] = {key: key for key in CANDLE_SIZES_MAPPER.keys()}

    return jsonify(response)


@dashboard.route('/trades', defaults={'page': None})
@dashboard.route('/trades/<page>')
def get_trades(page):

    response = {}

    orders = Trade.objects.all().order_by('open_time').values()

    paginator = Paginator(orders, 20)

    if page is None:
        page_obj = paginator.get_page(1)
        response["trades"] = list(page_obj)

    elif isinstance(page, int):
        page_obj = paginator.get_page(page)
        response["trades"] = list(page_obj)

    response["trades"] = [
        {TRADE_FORMAT_CONVERTER[key]: value for key, value in trade.items() if key in TRADE_FORMAT_CONVERTER}
        for trade in response["trades"]
    ]

    return jsonify(response)


@dashboard.route('/pipelines', defaults={'page': None})
@dashboard.route('/pipelines/<page>')
def get_pipelines(page):

    response = {}

    pipelines = Pipeline.objects.all().order_by('id').values()

    paginator = Paginator(pipelines, 20)

    if page is None:
        page_obj = paginator.get_page(1)
        response["pipelines"] = list(page_obj)

    elif isinstance(page, int):
        page_obj = paginator.get_page(page)
        response["pipelines"] = list(page_obj)

    response["pipelines"] = [
        {PIPELINE_FORMAT_CONVERTER[key]["name"]: PIPELINE_FORMAT_CONVERTER[key]["value_converter"](value)
         for key, value in pipeline.items() if key in PIPELINE_FORMAT_CONVERTER}
        for pipeline in response["pipelines"]
    ]

    return jsonify(response)


@dashboard.route('/positions', defaults={'page': None})
@dashboard.route('/positions/<page>')
def get_positions(page):

    response = {}

    positions = Position.objects.all().order_by('id').values()

    paginator = Paginator(positions, 100)

    if page is None:
        page_obj = paginator.get_page(1)
        response["positions"] = list(page_obj)

    elif isinstance(page, int):
        page_obj = paginator.get_page(page)
        response["positions"] = list(page_obj)

    response["positions"] = [
        {POSITION_FORMAT_CONVERTER[key]: value for key, value in position.items() if key in POSITION_FORMAT_CONVERTER}
        for position in response["positions"]
    ]

    return jsonify(response)

