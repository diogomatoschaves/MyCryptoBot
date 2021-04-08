


import os
from datetime import datetime
from dateutil.parser import parse

import pytz
import requests
import django

from data.extract.messari import get_headers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Asset, AssetResources


url = "https://data.messari.io/api/v1/assets"


asset_metrics = {
    "symbol": lambda coin: coin["symbol"],
    "name": lambda coin: coin["name"],
    "slug": lambda coin: coin["slug"],

    "category": lambda coin: coin["profile"]["category"],
    "sector": lambda coin: coin["profile"]["sector"],
    "overview": lambda coin: coin["profile"]["overview"],
    "technology": lambda coin: coin["profile"]["technology"],
    "tagline": lambda coin: coin["profile"]["tagline"],

    "all_time_high_price": lambda coin: coin["metrics"]["all_time_high"]["price"],
    "all_time_high_date": lambda coin: parse(coin["metrics"]["all_time_high"]["at"]).astimezone(pytz.timezone('UTC'))
                            if coin["metrics"]["all_time_high"]["at"] else None,
    "developer_activity_stars": lambda coin: coin["metrics"]["developer_activity"]["stars"],
    "developer_activity_commits_last_3_months": lambda coin: coin["metrics"]["developer_activity"]["commits_last_3_months"],
    "developer_activity_commits_last_1_year": lambda coin: coin["metrics"]["developer_activity"]["commits_last_1_year"],
    "asset_created_at": lambda coin: parse(coin["metrics"]["misc_data"]["asset_created_at"]).astimezone(pytz.timezone('UTC'))
                            if coin["metrics"]["misc_data"]["asset_created_at"] else None,

    "token_usage": lambda coin: coin["profile"]["token_details"]["usage"],
    "token_type": lambda coin: coin["profile"]["token_details"]["type"],
    "token_launch_style": lambda coin: coin["profile"]["token_details"]["launch_style"],
    "token_initial_supply": lambda coin: coin["profile"]["token_details"]["initial_supply"],
    "token_is_treasury_decentralized": lambda coin: coin["profile"]["token_details"]["is_treasury_decentralized"],
    "token_mining_algorithm": lambda coin: coin["profile"]["token_details"]["mining_algorithm"],
    "token_next_halving_date": lambda coin: coin["profile"]["token_details"]["next_halving_date"],
    "token_emission_type_general": lambda coin: coin["profile"]["token_details"]["emission_type_general"],
    "token_emission_type_precise": lambda coin: coin["profile"]["token_details"]["emission_type_precise"],
    "token_max_supply": lambda coin: coin["profile"]["token_details"]["max_supply"],
}


def process_response(response, time):

    coins = response["data"]

    if coins is None:
        print("emtpty values object")
        return
    else:
        print(len(coins))

    ordered_coins = sorted(coins, key=lambda x: x["metrics"]["marketcap"]["marketcap_dominance_percent"], reverse=True)

    for order, coin in enumerate(ordered_coins):

        kwargs = {attr: asset_metrics[attr](coin) for attr in asset_metrics}

        obj = Asset(stats_date=time, market_cap_ranking=order+1, **kwargs)

        obj.save()

        if coin["profile"]["relevant_resources"]:
            for resource in coin["profile"]["relevant_resources"]:

                name = resource["name"]
                url = resource["url"]

                resource_obj = AssetResources.objects.get_or_create(name=name, url=url)[0]

                obj.relevant_resources.add(resource_obj)

            obj.save()


def get_messari_data(limit):

    for page in range(1, 6):

        time = datetime.utcnow()

        query_params = {
            "limit": limit,
            "page": page
        }

        r = requests.get(url, headers=get_headers(), params=query_params)
        response = r.json()

        process_response(response, time)


if __name__ == "__main__":

    get_messari_data(limit=500)

