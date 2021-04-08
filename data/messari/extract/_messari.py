

import os
from datetime import datetime, timedelta

import pytz
import requests
import django

from data.messari import get_headers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Asset, MessariAPI


url = "https://data.messari.io/api/v1/assets/1e31218a-e44e-4285-820c-8282ee222035"


messari_metrics = {
    "price": {
        "schemma": ["open", "high", "low", "close", "volume"],
        "interval": '1m',
        "time_frame": {'hours': int(500 / 60)}
    },
    # "reddit.active.users": {
    #     "schemma": ["reddit_users"],
    #     "interval": '1h',
    #     "end_date": datetime(2020, 4, 29, 8, 0),
    #     "time_frame": 'hours'
    # },
    # "reddit.subscribers": {
    #     "schemma": ["reddit_subscribers"],
    #     "interval": '1h',
    #     "time_frame": 'hours'
    # },
    # "bitwise.volume": {
    #     "schemma": ["bitwise_volume"],
    #     "interval": '1h',
    #      "time_frame": 'hours'
    # },
    # "real.vol": {
    #     "schemma": ["real_volume"],
    #     "interval": '1h',
    #     "time_frame": 'hours'
    # },
    # "txn.tsfr.val.avg": {
    #     "schemma": ["average_transfer_value_usd"],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "exch.flow.out.usd.incl": {
    #     "schemma": ['flow_out_usd'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "exch.flow.in.usd.incl": {
    #     "schemma": ['flow_in_usd'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "txn.tsfr.cnt": {
    #     "schemma": ['transfers_count'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "txn.vol": {
    #     "schemma": ['transfers_volume'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "act.addr.cnt": {
    #     "schemma": ['active_addresses'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "blk.cnt": {
    #     "schemma": ['blocks_count'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "txn.cnt": {
    #     "schemma": ['transactions_count'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "diff.avg": {
    #     "schemma": ['mean_difficulty'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
    # "daily.shp": {
    #     "schemma": ['sharpe_30d', 'sharpe_90d', 'sharpe_1yr', 'sharpe_3yr'],
    #     "interval": '1d',
    #     "time_frame": 'days'
    # },
}

intervals = {
    '1h': 3600,
    '1d': 86400,
    '5m': 300
}


def process_response(response, metrics, schemma, interval, symbol='BTC'):

    values = response["data"]["values"]

    if values is None:
        print("emtpty values object")
        return

    for value in values:

        time = datetime.fromtimestamp(value[0] / 1000).astimezone(pytz.timezone('UTC'))
        asset = Asset.objects.get(symbol=symbol)

        kwargs = {metric: value[i + 1] for i, metric in enumerate(schemma)}

        if not MessariAPI.objects.filter(asset=asset, time=time, interval=interval).exists():

            obj = MessariAPI(
                time=time,
                asset=asset,
                interval=interval,
                **kwargs
            )
            obj.save()

        else:
            MessariAPI.objects.filter(asset=asset, time=time).update(**kwargs)


def get_messari_data(metric, schemma, beg=None, end=None, interval='1h'):

    uri = os.path.join(url, f"metrics/{metric}/time-series")

    query_params = {
        "beg": beg,
        "end": end,
        "interval": interval
    }

    r = requests.get(uri, headers=get_headers(), params=query_params)
    response = r.json()

    process_response(response, metric, schemma, intervals[interval])


if __name__ == "__main__":

    start = datetime(2019, 9, 1)

    for metric, metric_details in messari_metrics.items():

        print(metric)

        if "end_date" in metric_details:
            end = metric_details["end_date"]
        else:
            # end = datetime(2019, 10, 2)
            end = datetime.utcnow()

        beg = end - timedelta(**metric_details["time_frame"])

        while end > start:

            print(end)

            beg_iso = beg.isoformat()
            end_iso = end.isoformat()

            get_messari_data(
                beg=beg_iso,
                end=end_iso,
                metric=metric,
                interval=metric_details["interval"],
                schemma=metric_details["schemma"],
            )

            end = beg
            beg = end - timedelta(**metric_details["time_frame"])
