

import os
from datetime import datetime, timedelta

import requests
import django

from data.extract.scrapers.santiment.headers import headers, query

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

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


intervals_dict = {
    'minutes': {
        "delay": lambda x: 1000 / (60 / x) * 3600,
        "interval": lambda x: f"{x}m"
    }
}


if __name__ == "__main__":

    interval = 5
    interval_time_frame = 'minutes'

    # metric = 'active_addresses_1h'
    metric = 'volume_usd'
    time_delay = dict(seconds=intervals_dict[interval_time_frame]["delay"](interval))

    start = datetime(2019, 9, 1)

    end = datetime.utcnow()

    beg = end - timedelta(**time_delay)

    while end > start:

        print(end)

        beg_iso = f"{beg.isoformat()[:-3]}Z"
        end_iso = f"{end.isoformat()[:-3]}Z"

        get_santiment_data(
            beg=beg_iso,
            end=end_iso,
            metric=metric,
            interval=intervals_dict[interval_time_frame]["interval"](interval)
        )

        end = beg
        beg = end - timedelta(**time_delay)
