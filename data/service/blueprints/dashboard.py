import os
from functools import reduce

import django
from django.core.paginator import Paginator
from django.db.models import Count, Max, Avg, F, Min, Q, Sum
from flask import Blueprint, jsonify, request

from data.service.external_requests import get_strategies
from data.service.helpers._helpers import convert_queryset_to_dict, convert_trades_to_dict
from shared.exchanges.binance.constants import CANDLE_SIZES_MAPPER

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Exchange, Pipeline, Position, Trade

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

    orders = Trade.objects.filter(close_time__isnull=False).order_by('-open_time')

    paginator = Paginator(orders, 20)

    if page is None:
        page_obj = paginator.get_page(1)
        response["trades"] = list(page_obj)

    else:
        try:
            page_number = int(page)
            page_obj = paginator.get_page(page_number)
            response["trades"] = list(page_obj)
        except ValueError:
            return jsonify(response)

    response["trades"] = [trade.as_json() for trade in response["trades"]]

    return jsonify(response)


@dashboard.route('/pipelines', defaults={'page': None}, methods=["GET", "DELETE"])
@dashboard.route('/pipelines/<page>')
def handle_pipelines(page):

    response = {"message": "This method is not allowed", "success": False}

    pipeline_id = request.args.get("pipelineId", None)

    if request.method == 'GET':

        if Pipeline.objects.filter(id=pipeline_id).exists():
            response["pipelines"] = [pipeline.as_json() for pipeline in Pipeline.objects.filter(id=pipeline_id)]

        else:
            pipelines = Pipeline.objects.all().order_by('id')

            paginator = Paginator(pipelines, 20)

            if page is None:
                page_obj = paginator.get_page(1)
                response["pipelines"] = list(page_obj)

            elif isinstance(page, int):
                page_obj = paginator.get_page(page)
                response["pipelines"] = list(page_obj)

            response["pipelines"] = [pipeline.as_json() for pipeline in response["pipelines"]]

        response.update({"message": "The request was successful.", "success": True})

    if request.method == 'DELETE':
        if Pipeline.objects.filter(id=pipeline_id).exists():
            Pipeline.objects.filter(id=pipeline_id).delete()
            response.update({"message": "The trading bot was deleted", "success": True})
        else:
            response.update({"message": "The requested trading bot was not found", "success": False})

    return jsonify(response)


@dashboard.route('/positions', defaults={'page': None})
@dashboard.route('/positions/<page>')
def get_positions(page):

    response = {}

    positions = Position.objects.filter(open=True).order_by('id')

    paginator = Paginator(positions, 100)

    if page is None:
        page_obj = paginator.get_page(1)
        response["positions"] = list(page_obj)

    elif isinstance(page, int):
        page_obj = paginator.get_page(page)
        response["positions"] = list(page_obj)

    response["positions"] = [position.as_json() for position in response["positions"]]

    return jsonify(response)


@dashboard.route('/trades-metrics', methods=["GET"])
def get_trades_metrics():

    aggregate_values = Trade.objects.annotate(
        duration=F('close_time') - F('open_time'),
        winning_trade=Count('profit_loss', filter=Q(profit_loss__gte=0)),
        losing_trade=Count('profit_loss', filter=Q(profit_loss__lt=0))
    ).aggregate(
        Max('duration'),
        Avg('duration'),
        Count('id'),
        Max('profit_loss'),
        Min('profit_loss'),
        Sum('winning_trade'),
        Sum('losing_trade'),
    )

    aggregate_values = convert_trades_to_dict(aggregate_values)

    return jsonify(aggregate_values)


@dashboard.route('/pipelines-metrics', methods=["GET"])
def get_pipelines_metrics():

    def reduce_pipelines(accum, pipeline):

        trades_metrics = convert_trades_to_dict(pipeline.trade_set.all().annotate(
            duration=F('close_time') - F('open_time'),
            winning_trade=Count('profit_loss', filter=Q(profit_loss__gte=0)),
            losing_trade=Count('profit_loss', filter=Q(profit_loss__lt=0))
        ).aggregate(
            Max('duration'),
            Avg('duration'),
            Count('id'),
            Max('profit_loss'),
            Min('profit_loss'),
            Sum('winning_trade'),
            Sum('losing_trade'),
        ))

        win_rate = trades_metrics["winningTrades"] / trades_metrics["numberTrades"]

        return {
            **accum,
            str(pipeline.id): trades_metrics,
            "totalPipelines": accum["totalPipelines"] + 1,
            "activePipelines": accum["activePipelines"] + 1 if pipeline.active else accum["activePipelines"],
            "bestWinRate": {**pipeline.as_json(), "winRate": win_rate}
            if win_rate > accum["bestWinRate"]["winRate"] else accum["bestWinRate"],
            "mostTrades": {**pipeline.as_json(), "totalTrades": trades_metrics["numberTrades"]}
            if trades_metrics["numberTrades"] > accum["mostTrades"]["totalTrades"] else accum["mostTrades"],
        }

    pipelines = Pipeline.objects.all()

    pipelines_metrics = reduce(reduce_pipelines, pipelines, {
        "totalPipelines": 0,
        "activePipelines": 0,
        "bestWinRate": {"winRate": 0},
        "mostTrades": {"totalTrades": 0},
    })

    return jsonify(pipelines_metrics)
