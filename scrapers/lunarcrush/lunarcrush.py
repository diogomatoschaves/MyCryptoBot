import os
from datetime import datetime, timedelta

import pytz
import requests
import django

from scrapers.lunarcrush.headers import lunarcrush_headers
from scrapers.lunarcrush.session_key_handler import get_session_key

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crypto_db.settings")
django.setup()

from crypto_db.model.models import LunarCrushTimeEntries, Asset, LunarCrushInfluencer

url = 'https://api2.lunarcrush.com/v2'

endpoint_options = {
    1: {"data": "assets", "method": "assets", "dataset": lambda x: x["data"][0]["timeSeries"]},
    2: {"data": "influencers", "method": "influencers", "dataset": lambda x: x["data"]},
    3: {"data": "global", "method": "assets", "dataset": lambda x: x["data"]["timeSeries"]},
    4: {"data": "meta", "method": "meta", "dataset": lambda x: x["data"]},
}


assets_attributes = {
    'open',
    'close',
    'high',
    'low',
    'volume',
    'market_cap',
    'url_shares',
    'unique_url_shares',
    'reddit_posts',
    'reddit_posts_score',
    'reddit_comments',
    'reddit_comments_score',
    'tweets',
    'tweet_spam',
    'tweet_followers',
    'tweet_quotes',
    'tweet_retweets',
    'tweet_replies',
    'tweet_favorites',
    'tweet_sentiment1',
    'tweet_sentiment2',
    'tweet_sentiment3',
    'tweet_sentiment4',
    'tweet_sentiment5',
    'tweet_sentiment_impact1',
    'tweet_sentiment_impact2',
    'tweet_sentiment_impact3',
    'tweet_sentiment_impact4',
    'tweet_sentiment_impact5',
    'social_score',
    'average_sentiment',
    'sentiment_absolute',
    'sentiment_relative',
    'search_average',
    'news',
    'price_score',
    'social_impact_score',
    'correlation_rank',
    'galaxy_score',
    'volatility',
    'alt_rank',
    'alt_rank_30d',
    'market_cap_rank',
    'percent_change_24h_rank',
    'volume_24h_rank',
    'social_volume_24h_rank',
    'social_score_24h_rank',
    'medium',
    'youtube',
    'social_contributors',
    'social_volume',
    'price_btc',
    'social_volume_global',
    'social_dominance',
    'market_cap_global',
    'market_dominance',
    'percent_change_24h'
}


influencers_attributes = {
    "twitter_screen_name",
    "display_name",
    "volume",
    "followers",
    "following",
    "engagement",
    "volume_rank",
    "followers_rank",
    "engagement_rank",
}


def get_query_params(endpoint_option, symbol, data_points, interval, key, start, end):

    if endpoint_option == 1:
        return {
            "data": endpoint_options[endpoint_option]["data"],
            "symbol": symbol,
            "data_points": data_points,
            "interval": interval,
            "key": key,
            "start": start,
            "end": end
        }

    elif endpoint_option == 2:
        return {
            "data": endpoint_options[endpoint_option]["data"],
            "symbol": symbol,
            "days": data_points,
            "key": key,
            "order_by": 'influential'
        }

    elif endpoint_option == 3:
        return {
            "data": endpoint_options[endpoint_option]["data"],
            "data_points": data_points,
            "interval": interval,
            "key": key,
            "end": end,
        }

    elif endpoint_option == 4:
        return {
            "data": endpoint_options[endpoint_option]["data"],
            "key": key,
        }


def process_assets(time_series, symbol):

    asset = symbol

    for time_entry in time_series:

        time = datetime.fromtimestamp(time_entry["time"]).astimezone(pytz.timezone('UTC'))

        if not LunarCrushTimeEntries.objects.filter(asset=asset, time=time).exists():
            obj = LunarCrushTimeEntries(time=time, asset=asset, **{attr: time_entry[attr] for attr in assets_attributes if attr in time_entry})
            obj.save()


def process_influencers(influencers, symbol):

    asset = Asset.objects.get_or_create(symbol=symbol)[0]

    for influencer in influencers:

        obj = LunarCrushInfluencer(asset=asset, **{attr: influencer[attr] for attr in influencers_attributes if attr in influencer})
        obj.save()

    print(f'Processed {len(influencers)} influencers')


def process_feeds(response, symbol):

    asset = Asset.objects.get_or_create(symbol=symbol)[0]

    for influencer in response["data"]:

        obj = LunarCrushInfluencer(asset=asset, **{attr: influencer[attr] for attr in influencers_attributes if attr in influencer})
        obj.save()

    print(f'Processed {len(response["data"])} influencers')


def process_meta(dataset, symbol):

    for coin in dataset:
        asset_obj = Asset(name=coin["name"], symbol=coin["symbol"])
        asset_obj.save()


def get_lunarcrush_data(symbol, key, start=None, end=None, data_points=500, interval='hour', endpoint_option=1):

    uri = os.path.join(url, 'assets')

    query_params = get_query_params(endpoint_option, symbol, data_points, interval, key, start, end)

    r = requests.get(uri, headers=lunarcrush_headers, params=query_params)
    response = r.json()

    dataset = endpoint_options[endpoint_option]["dataset"](response)

    eval(f"process_{endpoint_options[endpoint_option]['method']}")(dataset, symbol)

    if endpoint_option in [1, 3]:
        return datetime.fromtimestamp(dataset[0]["time"])


if __name__ == "__main__":

    endpoint_option = 4
    symbol = "global"

    key = get_session_key()

    if endpoint_option in [1, 3]:

        end = datetime.utcnow() - timedelta(hours=1)

        start = datetime(2019, 9, 1)

        while end > start:

            print(end)

            end_timestamp = int(end.timestamp())

            end = get_lunarcrush_data(symbol, key, end=end_timestamp, endpoint_option=endpoint_option)

    elif endpoint_option == 2:

        get_lunarcrush_data(symbol, key, data_points=365, endpoint_option=endpoint_option)

    elif endpoint_option == 4:

        get_lunarcrush_data(symbol, key, endpoint_option=endpoint_option)
