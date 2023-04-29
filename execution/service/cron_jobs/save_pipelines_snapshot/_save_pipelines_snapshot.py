import logging
import os
from datetime import datetime

import django
import pytz

from execution.service.blueprints.market_data import get_ticker

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

    for position in open_positions:

        binance_obj = binance_trader_objects[0] if position.paper_trading else binance_trader_objects[1]

        symbol = position.symbol.name

        time = datetime.now(pytz.utc)

        response = get_ticker(position.symbol.name)

        if response is None:
            continue

        current_price = float(response["price"])

        try:
            current_value = binance_obj.current_balance[symbol] + binance_obj.units[symbol] * current_price

            PortfolioTimeSeries.objects.create(pipeline=position.pipeline, time=time, value=current_value)

        except TypeError:
            continue
