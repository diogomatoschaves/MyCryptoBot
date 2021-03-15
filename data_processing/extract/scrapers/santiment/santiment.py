

import os
from datetime import datetime, timedelta
import urllib

import pytz
import requests
import django

from data_processing.extract.scrapers.messari.headers import get_headers
from data_processing.extract.scrapers.santiment.headers import headers, query

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Asset, MessariAPI


url = "https://api.santiment.net/graphql"


def process_response(response, symbol='BTC'):

    pass


def get_santiment_data(metric, beg=None, end=None, interval='1h', slug='bitcoin'):

    request_payload = {
        "operationName": "getMetric",
        "query": query,
        "variables": {
            "metric": metric,
            "interval": interval,
            "slug": slug,
            "from": beg,
            "to": end
        }
    }

    r = requests.post(url, headers=headers, json=request_payload)
    response = r.json()

    process_response(response)


if __name__ == "__main__":

    metric = 'active_addresses_1h'
    time_frame = 'hours'
    time_limit = 1000

    start = datetime(2019, 9, 1)

    end = datetime.utcnow() - timedelta(hours=1)

    beg = end - timedelta(**{time_frame: time_limit})

    while end > start:

        print(end)

        beg_iso = f"{beg.isoformat()[:-3]}Z"
        end_iso = f"{end.isoformat()[:-3]}Z"

        get_santiment_data(
            beg=beg_iso,
            end=end_iso,
            metric=metric,
        )

        end = beg
        beg = end - timedelta(**{time_frame: time_limit})
