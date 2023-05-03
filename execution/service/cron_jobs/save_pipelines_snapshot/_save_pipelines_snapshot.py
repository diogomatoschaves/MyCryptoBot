import logging
import os
from datetime import datetime

import django
import pytz

from execution.service.blueprints.market_data import get_ticker, get_balances

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import PortfolioTimeSeries, Position


def save_pipelines_snapshot(binance_trader_objects, pipeline_id=None):

    logging.debug('Saving pipelines snapshot...')

    filter_dict = {
        "pipeline__active": True
    }

    if pipeline_id is not None:
        filter_dict["pipeline__id"] = pipeline_id

    open_positions = Position.objects.filter(**filter_dict)

    time = datetime.now(pytz.utc)

    total_current_value = {
        'live': 0,
        'testnet': 0
    }
    for position in open_positions:

        binance_obj = binance_trader_objects[0] if position.paper_trading else binance_trader_objects[1]

        symbol = position.symbol.name

        response = get_ticker(position.symbol.name)

        if response is None:
            continue

        current_price = float(response["price"])

        try:
            current_value = binance_obj.current_balance[symbol] + binance_obj.units[symbol] * current_price

            initial_equity = position.pipeline.allocation
            leverage = position.pipeline.leverage

            current_value = (current_value - initial_equity) + initial_equity / leverage

            PortfolioTimeSeries.objects.create(pipeline=position.pipeline, time=time, value=current_value)

            key = 'testnet' if position.pipeline.paper_trading else 'live'

            total_current_value[key] += current_value

        except TypeError:
            continue

    if pipeline_id is None and len(open_positions) > 0:
        balances = get_balances()

        for account_type in balances:
            for asset in balances[account_type]:
                if asset['asset'] == 'USDT':

                    current_value = float(asset["withdrawAvailable"]) + total_current_value[account_type]

                    PortfolioTimeSeries.objects.create(time=time, value=current_value, type=account_type)
