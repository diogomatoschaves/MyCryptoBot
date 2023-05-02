import json
import os
from collections import defaultdict
from functools import reduce

import django
from django.core.paginator import Paginator
from django.db.models import Count, Max, Avg, F, Min, Q, Sum
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from data.service.external_requests import get_strategies
from data.service.helpers._helpers import convert_queryset_to_dict, convert_trades_to_dict, convert_client_request, \
    get_pipeline_equity_timeseries
from shared.exchanges.binance.constants import CANDLE_SIZES_MAPPER, CANDLE_SIZES_ORDERED
from shared.utils.decorators import handle_db_connection_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Exchange, Pipeline, Position, Trade, PortfolioTimeSeries

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/resources/<resources>')
@jwt_required()
@handle_db_connection_error
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
            response["candleSizes"] = CANDLE_SIZES_ORDERED

    return jsonify(response)


@dashboard.route('/trades', defaults={'page': None}, methods=["GET"])
@dashboard.route('/trades/<page>')
@jwt_required()
@handle_db_connection_error
def get_trades(page):

    args = request.args

    response = {}

    trades = Trade.objects.filter(close_time__isnull=False).order_by('-open_time')
    if "pipelineId" in args:
        trades = trades.filter(pipeline__id=args["pipelineId"])

    paginator = Paginator(trades, 20)

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


@dashboard.route('/pipelines', defaults={'page': None}, methods=["GET", "PUT", "DELETE"])
@dashboard.route('/pipelines/<page>')
@handle_db_connection_error
@jwt_required()
def handle_pipelines(page):

    response = {"message": "This method is not allowed", "success": False}

    pipeline_id = request.args.get("pipelineId", None)

    if request.method == 'GET':

        if Pipeline.objects.filter(id=pipeline_id).exists():
            response["pipelines"] = [pipeline.as_json() for pipeline in Pipeline.objects.filter(id=pipeline_id)]

        else:
            pipelines = Pipeline.objects.filter(deleted=False).order_by('id')

            paginator = Paginator(pipelines, 20)

            if page is None:
                page_obj = paginator.get_page(1)
                response["pipelines"] = list(page_obj)

            elif isinstance(page, int):
                page_obj = paginator.get_page(page)
                response["pipelines"] = list(page_obj)

            response["pipelines"] = [pipeline.as_json() for pipeline in response["pipelines"]]

        response.update({"message": "The request was successful.", "success": True})

    elif request.method == 'DELETE':
        if Pipeline.objects.filter(id=pipeline_id).exists():
            Pipeline.objects.filter(id=pipeline_id).update(deleted=True)
            response.update({"message": "The trading bot was deleted", "success": True})
        else:
            response.update({"message": "The requested trading bot was not found", "success": True})

    elif request.method == 'PUT':
        if Pipeline.objects.filter(id=pipeline_id).exists():
            data = request.get_json(force=True)

            data = convert_client_request(data)

            Pipeline.objects.filter(id=pipeline_id).update(**data)
            pipeline = Pipeline.objects.get(id=pipeline_id)
            response.update({
                "message": "The trading bot was updated successfully.",
                "success": True,
                "pipeline": pipeline.as_json()
            })
        else:
            response.update({"message": "The requested trading bot was not found", "success": False})

    return jsonify(response)


@dashboard.route('/positions', defaults={'page': None})
@dashboard.route('/positions/<page>')
@jwt_required()
@handle_db_connection_error
def get_positions(page):

    response = {}

    positions = Position.objects.filter(pipeline__active=True).order_by('id')

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
@jwt_required()
@handle_db_connection_error
def get_trades_metrics():

    aggregate_values = Trade.objects.exclude(close_time=None).annotate(
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
@jwt_required()
@handle_db_connection_error
def get_pipelines_metrics():

    def reduce_pipelines(accum, pipeline):

        try:
            trades_metrics = convert_trades_to_dict(pipeline.trade_set.exclude(close_time=None).annotate(
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

            try:
                win_rate = trades_metrics["winningTrades"] / trades_metrics["numberTrades"]
            except TypeError:
                win_rate = None

            return {
                **accum,
                str(pipeline.id): trades_metrics,
                "totalPipelines": accum["totalPipelines"] + 1,
                "activePipelines": accum["activePipelines"] + 1 if pipeline.active else accum["activePipelines"],
                "bestWinRate": {**pipeline.as_json(), "winRate": win_rate}
                if win_rate and win_rate > accum["bestWinRate"]["winRate"] else accum["bestWinRate"],
                "mostTrades": {**pipeline.as_json(), "totalTrades": trades_metrics["numberTrades"]}
                if trades_metrics["numberTrades"] > accum["mostTrades"]["totalTrades"] else accum["mostTrades"],
            }
        except AttributeError:
            return {
                **accum,
                "totalPipelines": accum["totalPipelines"] + 1,
                "activePipelines": accum["activePipelines"] + 1 if pipeline.active else accum["activePipelines"],
            }

    pipelines = Pipeline.objects.exclude(deleted=True)

    pipelines_metrics = reduce(reduce_pipelines, pipelines, {
        "totalPipelines": 0,
        "activePipelines": 0,
        "bestWinRate": {"winRate": 0},
        "mostTrades": {"totalTrades": 0},
    })

    return jsonify(pipelines_metrics)


@dashboard.route('/pipeline-equity', methods=["GET"], defaults={'pipeline_id': None})
@dashboard.route('/pipeline-equity/<pipeline_id>')
@jwt_required()
@handle_db_connection_error
def get_pipeline_equity(pipeline_id):

    time_frame = request.args.get("timeFrame", '1h')

    try:
        time_frame_converted = CANDLE_SIZES_MAPPER[time_frame]
    except KeyError:
        return jsonify({"success": False, "message": "The provided time frame is not valid."})

    if pipeline_id:

        data = get_pipeline_equity_timeseries(pipeline_id=pipeline_id, time_frame_converted=time_frame_converted)

        return jsonify({"success": True, "data": data})

    else:
        data = {
            'live': [],
            'testnet': []
        }

        for account_type in data:

            data[account_type] = get_pipeline_equity_timeseries(
                account_type=account_type,
                time_frame_converted=time_frame_converted
            )

        return jsonify({"success": True, "data": data})


@dashboard.route('/pipelines-pnl', methods=["GET"], defaults={'pipeline_ids': ''})
@dashboard.route('/pipelines-pnl/<pipeline_ids>')
@jwt_required()
@handle_db_connection_error
def get_pipeline_pnl(pipeline_ids):

    pipeline_ids = [int(pipeline_id) for pipeline_id in pipeline_ids.split(',')]

    pipelines_pnl = defaultdict(lambda: {})
    for pipeline_id in pipeline_ids:
        first = PortfolioTimeSeries.objects.filter(pipeline__id=pipeline_id).first()
        last = PortfolioTimeSeries.objects.filter(pipeline__id=pipeline_id).last()

        if first and last:
            pipelines_pnl[pipeline_id]["profit"] = round((last.value - first.value), 2)
            pipelines_pnl[pipeline_id]["pnl"] = round((last.value - first.value) / (first.value / first.pipeline.leverage) * 100, 2)

    return jsonify({"success": True, "pipelinesPnl": pipelines_pnl})
