import os
from itertools import combinations
from datetime import timedelta, datetime

import django
from dateutil.parser import parse
from scrapers.twitter.tweets_fetcher import get_tweets

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crypto_db.settings")
django.setup()

from database.model.models import Tweet, TwitterUser, Hashtag, LunarCrushTimeEntries


def daterange(start_date, end_date):

    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def process_users(users):

    user_ids = set()

    for user_id, user in users.items():

        user_ids.add(user_id)

        created_at = parse(user["created_at"])

        user_obj = TwitterUser(
            id = user_id,
            name = user["name"],
            location = user["location"],
            description = user["description"],
            followers_count = user["followers_count"],
            friends_count = user["friends_count"],
            listed_count = user["listed_count"],
            created_at = created_at,
            favourites_count = user["favourites_count"],
            statuses_count = user['statuses_count'],
            media_count = user["media_count"],
            blocked_by = user["blocked_by"],
            blocking = user["blocking"]
        )

        user_obj.save()

    return user_ids


def process_tweets(tweets):

    tweet_ids = set()

    for tweet_id, tweet in tweets.items():

        tweet_ids.add(tweet_id)

        created_at = parse(tweet["created_at"])
        user = TwitterUser.objects.get(id=tweet["user_id_str"])

        tweet_obj = LunarCrushTimeEntries(
            id = tweet_id,
            created_at = created_at,
            full_text = tweet["full_text"],
            number_hashtags = len(tweet["entities"]["hashtags"]),
            number_symbols = len(tweet["entities"]["symbols"]),
            user_mentions = len(tweet["entities"]["user_mentions"]),
            number_urls = len(tweet["entities"]["urls"]),
            number_media = len(tweet["entities"]["media"]) if "media" in tweet["entities"] else 0,
            user = user,
            in_reply_to_status = True if tweet['in_reply_to_status_id'] else False,
            has_quoted_status = True if tweet['is_quote_status'] in tweet else False,
            contributors = tweet["contributors"],
            retweet_count = tweet["retweet_count"],
            favourite_count = tweet["favorite_count"],
            reply_count = tweet["reply_count"],
            quote_count = tweet["quote_count"],
            possibly_sensitive = tweet["possibly_sensitive"] if "possibly_sensitive" in tweet else False
        )

        tweet_obj.save()

        for hashtag in tweet["entities"]["hashtags"]:
            hashtag_obj = Hashtag.objects.get_or_create(name=hashtag["text"].lower())[0]

            tweet_obj.hashtags.add(hashtag_obj)

    return tweet_ids


def process_response(user_ids, tweet_ids, response):

    new_user_ids = process_users(response["globalObjects"]["users"])

    new_tweet_ids = process_tweets(response["globalObjects"]["tweets"])

    user_ids = user_ids.union(new_user_ids)
    tweet_ids = tweet_ids.union(new_tweet_ids)

    return user_ids, tweet_ids


def combine_search(words, hashtags, from_date, until_date, user_ids, tweet_ids):

    comb_words = ['a']
    comb_hashtags = ['a']
    i = 1

    while len(comb_words) != 0 or len(comb_hashtags) != 0:
        comb_words = list(combinations(words, i))
        comb_hashtags = list(combinations(hashtags, i))

        for word_comb in comb_words:
            response = get_tweets(word_comb, [], from_date, until_date)

            try:
                user_ids, tweet_ids = process_response(user_ids, tweet_ids, response)
            except KeyError:
                response = get_tweets(word_comb, [], from_date, until_date)

        for hashtag_comb in comb_hashtags:
            response = get_tweets([], hashtag_comb, from_date, until_date)

            try:
                user_ids, tweet_ids = process_response(user_ids, tweet_ids, response)
            except KeyError:
                response = get_tweets([], hashtag_comb, from_date, until_date)

        i += 1

    return user_ids, tweet_ids


def fetch_twitter_data(start_date, end_date, words, hashtags):

    for single_date in daterange(start_date, end_date):

        from_date = single_date.strftime("%Y-%m-%d")
        until_date = (single_date + timedelta(days=1)).strftime("%Y-%m-%d")

        print(from_date)

        user_ids = set()
        tweet_ids = set()

        user_ids, tweet_ids = combine_search(words, [], from_date, until_date, user_ids, tweet_ids)
        user_ids, tweet_ids = combine_search([], hashtags, from_date, until_date, user_ids, tweet_ids)

        print(f'New Tweets: {len(tweet_ids)}')
        print(f'New Users: {len(user_ids)}')
        print()


if __name__ == '__main__':

    start_date = '2020-02-17'
    end_date = '2021-02-21'

    words = ["bitcoin", "bitcoins", "btc"]
    hashtags = ["cryptocurrency", "bitcoin", "btc"]

    fetch_twitter_data(start_date, end_date, words, hashtags)
