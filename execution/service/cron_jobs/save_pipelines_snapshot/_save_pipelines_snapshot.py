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

    balances = get_account_data()

    for account_type, account_balances in balances.items():

        net_account_balance = float(account_balances["totalWalletBalance"]) - float(account_balances["totalUnrealizedProfit"])
        PortfolioTimeSeries.objects.create(time=time, value=net_account_balance, type=account_type)

        for symbol in symbols[account_type]:

            position = [balance for balance in account_balances["positions"] if balance["symbol"] == symbol["symbol"]][0]

            save_pipeline_snapshot(symbol["pipeline_id"], float(position["unrealizedProfit"]))


def save_pipeline_snapshot(pipeline_id, unrealized_profit=0):

    pipeline = Pipeline.objects.get(id=pipeline_id)

    time = datetime.now(pytz.utc)

    equity = pipeline.current_equity + unrealized_profit

    PortfolioTimeSeries.objects.create(pipeline=pipeline, time=time, value=equity)
