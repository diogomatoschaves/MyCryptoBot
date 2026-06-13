import logging
import os
from datetime import datetime

import django
import pytz

from execution.service.blueprints.market_data import get_account_data
from shared.utils.decorators import handle_db_connection_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import PortfolioTimeSeries, Pipeline, Position


def parse_balance(value):
    # An unfunded or inactive futures account can return '' for balance fields.
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@handle_db_connection_error
def save_portfolio_value_snapshot():
    logging.debug('Saving pipelines snapshot...')

    open_positions_test = Position.objects.filter(pipeline__active=True, pipeline__paper_trading=True)
    open_positions_live = Position.objects.filter(pipeline__active=True, pipeline__paper_trading=False)

    if len(open_positions_live) == 0 and len(open_positions_test) == 0:
        return

    time = datetime.now(pytz.utc)

    symbols = dict()

    symbols["testnet"] = [{"symbol": position.pipeline.symbol.name, "pipeline_id": position.pipeline.id} for position in open_positions_test]
    symbols["live"] = [{"symbol": position.pipeline.symbol.name, "pipeline_id": position.pipeline.id} for position in open_positions_live]

    account_types = [account_type for account_type, account_symbols in symbols.items() if account_symbols]

    balances = get_account_data(account_types)

    for account_type, account_balances in balances.items():

        net_account_balance = (
            parse_balance(account_balances.get("totalWalletBalance"))
            - parse_balance(account_balances.get("totalUnrealizedProfit"))
        )
        PortfolioTimeSeries.objects.create(time=time, value=net_account_balance, type=account_type)

        for symbol in symbols[account_type]:

            position = next(
                (balance for balance in account_balances.get("positions", []) if balance["symbol"] == symbol["symbol"]),
                None,
            )

            unrealized_profit = parse_balance(position["unrealizedProfit"]) if position else 0.0

            save_pipeline_snapshot(symbol["pipeline_id"], unrealized_profit)


def save_pipeline_snapshot(pipeline_id, unrealized_profit=0):

    pipeline = Pipeline.objects.get(id=pipeline_id)

    time = datetime.now(pytz.utc)

    equity = pipeline.current_equity + unrealized_profit

    PortfolioTimeSeries.objects.create(pipeline=pipeline, time=time, value=equity)
