import os
import time
from collections import defaultdict

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
from shared.utils.notifier import (
    send_alert,
    get_telegram_credentials,
    TELEGRAM_TOKEN_KEY,
    TELEGRAM_CHAT_ID_KEY,
)
import shared.utils.notifier as notifier

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Exchange, Pipeline, Position, Trade, AppSetting

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

    # cache strategies, but never cache a failed fetch (None) - otherwise a
    # transient model-app outage poisons the cache for the process lifetime
    STRATEGIES = globals().get("STRATEGIES")
    if not STRATEGIES:
        STRATEGIES = get_strategies()
        if STRATEGIES:
            globals()["STRATEGIES"] = STRATEGIES

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

        # one grouped count per symbol instead of a query per symbol
        symbol_counts = (
            Trade.objects.exclude(close_time=None)
            .values("pipeline__symbol")
            .annotate(value=Count("id"))
            .filter(value__gt=0)
            .order_by("pipeline__symbol")
        )

        aggregate_values["tradesCount"] = [
            {"name": row["pipeline__symbol"], "value": row["value"]}
            for row in symbol_counts
        ]

    return jsonify(aggregate_values)


@dashboard.get('/pipelines-metrics')
@general_app_error
@jwt_required()
@handle_db_connection_error
def get_pipelines_metrics():

    pipelines = Pipeline.objects.exclude(deleted=True)

    # per-pipeline trade counts in a single grouped query instead of one
    # aggregate query per pipeline
    trade_stats = {
        row["pipeline_id"]: row
        for row in Trade.objects.exclude(close_time=None)
        .values("pipeline_id")
        .annotate(
            number_trades=Count("id"),
            winning_trades=Count("pnl_pct", filter=Q(pnl_pct__gte=0)),
        )
    }

    metrics = {
        "totalPipelines": 0,
        "activePipelines": 0,
        "bestWinRate": {"winRate": 0},
        "mostTrades": {"totalTrades": 0},
    }

    for pipeline in pipelines:
        metrics["totalPipelines"] += 1
        if pipeline.active:
            metrics["activePipelines"] += 1

        stats = trade_stats.get(pipeline.id)
        if not stats:
            continue

        number_trades = stats["number_trades"]
        win_rate = stats["winning_trades"] / number_trades if number_trades else None

        if win_rate and win_rate > metrics["bestWinRate"]["winRate"]:
            metrics["bestWinRate"] = {**pipeline.as_json(), "winRate": win_rate}

        if number_trades > metrics["mostTrades"]["totalTrades"]:
            metrics["mostTrades"] = {**pipeline.as_json(), "totalTrades": number_trades}

    return jsonify(metrics)


@dashboard.get('/pipeline-equity', defaults={'pipeline_id': None})
@dashboard.get('/pipeline-equity/<pipeline_id>')
@general_app_error
@jwt_required()
@handle_db_connection_error
def get_pipeline_equity(pipeline_id):

    max_items = int(request.args.get("maxItems", 500))

    if pipeline_id:

        data = get_pipeline_equity_timeseries(pipeline_id=pipeline_id, max_items=max_items)

        return jsonify({"success": True, "data": data})

    else:
        data = {
            'live': [],
            'testnet': []
        }

        for account_type in data:

            data[account_type] = get_pipeline_equity_timeseries(
                account_type=account_type,
                max_items=max_items
            )

        return jsonify({"success": True, "data": data})


def _mask(value):
    return f"{value[:2]}***{value[-2:]}" if value and len(value) > 4 else ("***" if value else None)


@dashboard.get('/alerts')
@general_app_error
@jwt_required()
def get_alerts_status():
    """Reports whether Telegram alerting is configured and from which source
    (environment variables win over dashboard-saved settings). Only a masked
    chat id is ever exposed - never the bot token."""
    token, chat_id, source = get_telegram_credentials()

    return jsonify({
        "success": True,
        "configured": bool(token and chat_id),
        "source": source,
        "chatId": _mask(chat_id),
    })


@dashboard.put('/alerts')
@general_app_error
@jwt_required()
@handle_db_connection_error
def save_alerts_settings():
    """Saves the Telegram credentials from the dashboard. The token is
    write-only: it is stored server-side and never returned to the client.
    Sending empty strings clears the stored settings."""
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        return jsonify({
            "success": False,
            "message": (
                "Telegram alerts are configured through environment variables, "
                "which take precedence - update them in your deployment config instead."
            ),
        })

    request_data = request.get_json(force=True)

    bot_token = (request_data.get("botToken") or "").strip()
    chat_id = (request_data.get("chatId") or "").strip()

    if bool(bot_token) != bool(chat_id):
        return jsonify({
            "success": False,
            "message": "Both the bot token and the chat ID are required.",
        })

    AppSetting.objects.update_or_create(
        key=TELEGRAM_TOKEN_KEY, defaults={"value": bot_token}
    )
    AppSetting.objects.update_or_create(
        key=TELEGRAM_CHAT_ID_KEY, defaults={"value": chat_id}
    )

    # the notifier caches resolved credentials briefly - drop it so a test
    # alert right after saving uses the new values
    notifier._reset_state()

    if not bot_token:
        return jsonify({"success": True, "message": "Telegram settings cleared."})

    return jsonify({
        "success": True,
        "message": "Telegram settings saved - send a test alert to verify.",
    })


@dashboard.post('/alerts/test')
@general_app_error
@jwt_required()
def send_test_alert():
    """Sends a test alert so the user can verify their Telegram setup
    end-to-end from the dashboard."""
    sent = send_alert(
        title="Test alert",
        body=(
            "This is a test alert from your MyCryptoBot dashboard. "
            "Alerting is configured correctly."
        ),
        severity="info",
        # unique key: repeated test clicks must not be throttled away
        dedup_key=f"test-alert-{time.time()}",
    )

    if sent:
        return jsonify({
            "success": True,
            "message": "Test alert sent - check your Telegram.",
        })

    return jsonify({
        "success": False,
        "message": (
            "The alert could not be sent. Check the TELEGRAM_BOT_TOKEN and "
            "TELEGRAM_CHAT_ID environment variables and the data service logs."
        ),
    })
