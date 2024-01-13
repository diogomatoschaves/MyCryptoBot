import os
from collections import defaultdict
from functools import reduce

import django
from django.core.paginator import Paginator
from django.db.models import Count, Q
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from data.service.external_requests import get_strategies, get_price
from data.service.helpers import convert_queryset_to_dict, convert_trades_to_dict, convert_client_request, \
    get_pipeline_equity_timeseries, check_input, extract_request_params, add_strategies, query_trades_metrics
from shared.utils.decorators import general_app_error
from shared.exchanges.binance.constants import CANDLE_SIZES_MAPPER, CANDLE_SIZES_ORDERED
from shared.utils.decorators import handle_db_connection_error
from shared.utils.exceptions import NoSuchPipeline

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Exchange, Pipeline, Position, Trade

dashboard = Blueprint('dashboard', __name__)


@dashboard.get('/resources', defaults={'resources': None})
@dashboard.get('resources/<resources>')
@general_app_error
@jwt_required()
@handle_db_connection_error
def get_resources(resources):

    resources = ["symbols", "exchanges", "strategies", "candleSizes"] if resources is None else resources.split(',')

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


@dashboard.get('/trades', defaults={'page': None})
@dashboard.get('/trades/<page>')
@general_app_error
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
            response["trades"] = []

    response["trades"] = [trade.as_json() for trade in response["trades"]]

    return jsonify(response)


@dashboard.route('/pipelines', defaults={'page': None}, methods=["GET", "PUT", "DELETE"])
@dashboard.route('/pipelines/<page>', methods=["GET", "PUT", "DELETE"])
@general_app_error
@handle_db_connection_error
@jwt_required()
def handle_pipelines(page):

    if "STRATEGIES" not in globals():
        STRATEGIES = get_strategies()
        globals()["STRATEGIES"] = STRATEGIES
    else:
        STRATEGIES = globals()["STRATEGIES"]

    response = {"message": "This method is not allowed", "success": False}

    pipeline_id = request.args.get("pipelineId", None)

    if request.method == 'GET':

        response["pipelines"] = []

        if Pipeline.objects.filter(id=pipeline_id).exists():
            pipeline = Pipeline.objects.get(id=pipeline_id)
            response["pipelines"] = [pipeline.as_json()]

        else:
            pipelines = Pipeline.objects.filter(deleted=False).order_by('-last_entry')

            paginator = Paginator(pipelines, 20)

            if page is None:
                page_obj = paginator.get_page(1)
                response["pipelines"] = list(page_obj)

            else:
                try:
                    page_number = int(page)
                    page_obj = paginator.get_page(page_number)

                    response["pipelines"] = list(page_obj)
                except ValueError:
                    pass

            response["pipelines"] = [pipeline.as_json() for pipeline in response["pipelines"]]

        response.update({"message": "The request was successful.", "success": True})

    elif request.method == 'DELETE':
        if Pipeline.objects.filter(id=pipeline_id).exists():
            Pipeline.objects.filter(id=pipeline_id).update(deleted=True)
            response.update({"message": "The trading bot was deleted", "success": True})
        else:
            response.update({"message": "The requested trading bot was not found", "success": False})

    elif request.method == 'PUT':
        if Pipeline.objects.filter(id=pipeline_id).exists():
            request_data = extract_request_params(request)

            request_data["pipeline_id"] = pipeline_id

            check_input(STRATEGIES, edit_pipeline=True, **request_data)

            data = convert_client_request(request_data)

            Pipeline.objects.filter(id=pipeline_id).update(**data)
            pipeline = Pipeline.objects.get(id=pipeline_id)

            strategy_objs = add_strategies(request_data["strategy"])
            pipeline.strategy.set(strategy_objs)

            response.update({
                "message": "The trading bot was updated successfully.",
                "success": True,
                "pipeline": pipeline.as_json()
            })
        else:
            response.update({"message": "The requested trading bot was not found", "success": False})

    return jsonify(response)


@dashboard.get('/positions', defaults={'page': None})
@dashboard.get('/positions/<page>')
@general_app_error
@jwt_required()
@handle_db_connection_error
def get_positions(page):

    response = {"positions": []}

    positions = Position.objects.filter(pipeline__active=True).order_by('id')

    paginator = Paginator(positions, 100)

    if page is None:
        page_obj = paginator.get_page(1)
        response["positions"] = list(page_obj)

    else:
        try:
            page_number = int(page)
            page_obj = paginator.get_page(page_number)

            response["positions"] = list(page_obj)
        except ValueError:
            pass

    response["positions"] = [position.as_json() for position in response["positions"]]

    return jsonify(response)


@dashboard.get('/trades-metrics')
@general_app_error
@jwt_required()
@handle_db_connection_error
def get_trades_metrics():
    args = request.args

    try:
        if "pipelineId" in args:
            pipeline_id = args["pipelineId"]
            if Pipeline.objects.filter(id=pipeline_id).exists():
                pipeline = Pipeline.objects.get(id=pipeline_id)

                aggregate_values = convert_trades_to_dict(query_trades_metrics(pipeline))
            else:
                raise NoSuchPipeline
        else:
            raise NoSuchPipeline
    except NoSuchPipeline:
        aggregate_values = convert_trades_to_dict(query_trades_metrics())

        symbols_objs = Symbol.objects.annotate(trade_count=Count('trade', filter=~Q(trade__close_time=None)))
        symbols = []

        for symbol in symbols_objs:
            if symbol.trade_count > 0:
                symbol_dict = {"name": symbol.name, "value": symbol.trade_count}

                symbols.append(symbol_dict)

        aggregate_values["tradesCount"] = symbols

    return jsonify(aggregate_values)


@dashboard.get('/pipelines-metrics')
@general_app_error
@jwt_required()
@handle_db_connection_error
def get_pipelines_metrics():

    def reduce_pipelines(accum, pipeline):
        try:
            trades_metrics = convert_trades_to_dict(query_trades_metrics(pipeline))

            try:
                win_rate = trades_metrics["winningTrades"] / trades_metrics["numberTrades"]
            except TypeError:
                win_rate = None

            return {
                **accum,
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


@dashboard.get('/pipeline-equity', defaults={'pipeline_id': None})
@dashboard.get('/pipeline-equity/<pipeline_id>')
@general_app_error
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


@dashboard.get('/pipelines-pnl', defaults={'pipeline_ids': ''})
@dashboard.get('/pipelines-pnl/<pipeline_ids>')
@general_app_error
@jwt_required()
@handle_db_connection_error
def get_pipeline_pnl(pipeline_ids):

    try:
        pipeline_ids = [int(pipeline_id) for pipeline_id in pipeline_ids.split(',')]
    except ValueError:
        return jsonify({"success": False, "pipelinesPnl": {}})

    pipelines = Pipeline.objects.filter(id__in=pipeline_ids)

    pipelines_pnl = defaultdict(lambda: {})
    for pipeline in pipelines:

        if pipeline.active:

            response = get_price(pipeline.symbol.name)

            if not response or ("success" in response and not response["success"]):
                continue

            price = float(response["price"])

        else:
            if Trade.objects.filter(pipeline__id=pipeline.id).exists():
                last_trade = Trade.objects.filter(pipeline__id=pipeline.id).last()
                price = last_trade.close_price
            else:
                continue

        try:
            current_value = pipeline.balance + pipeline.units * price

            leverage = pipeline.leverage
            initial_equity = pipeline.equity
            leveraged_equity = initial_equity * leverage

            profit = (current_value - leveraged_equity)
            pnl = profit / initial_equity

            pipelines_pnl[pipeline.id]["profit"] = round(profit, 2)
            pipelines_pnl[pipeline.id]["pnl"] = round(pnl * 100, 2)

        except TypeError:
            continue

    return jsonify({"success": True, "pipelinesPnl": pipelines_pnl})
