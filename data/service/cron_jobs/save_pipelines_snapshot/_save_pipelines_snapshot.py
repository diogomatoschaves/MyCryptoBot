import logging
import os
from datetime import datetime

import django
import pytz

from data.service.external_requests import get_price

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import PortfolioTimeSeries, Position


def save_pipelines_snapshot(pipeline_id=None):

    logging.debug('Saving pipelines snapshot...')

    filter_dict = {
        "pipeline__active": True
    }

    if pipeline_id is not None:
        filter_dict["pipeline__id"] = pipeline_id

    open_positions = Position.objects.filter(**filter_dict)

    for position in open_positions:

        time = datetime.now(pytz.utc)

        current_price = float(get_price(position.symbol.name)["price"])

        try:
            current_value = position.buying_price * position.amount * \
                            (1 + position.position * (1 - current_price / position.buying_price))

            PortfolioTimeSeries.objects.create(pipeline=position.pipeline, time=time, value=current_value)

        except TypeError:
            continue
