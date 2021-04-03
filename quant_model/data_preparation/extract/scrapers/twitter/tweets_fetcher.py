import requests
from requests.exceptions import ConnectionError

from quant_model.data_preparation.extract.scrapers import get_twitter_headers


def get_tweets(words, hashtags, from_date, until_date, min_favs=None):

    headers = get_twitter_headers()

    words_string = '(' + '%20OR%20'.join(words) + ')%20'

    hashtags_string = '(' + '%20OR%20'.join(['%23' + hashtag for hashtag in hashtags]) + ')%20'

    if not min_favs:
        min_favs_string = ''
    else:
        min_favs_string = f'min_faves%3A{min_favs}%20'

    query_string = f"include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&" \
                   "include_followed_by=1&include_want_retweets=1&include_mute_edge=1&" \
                   "include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12&" \
                   "include_cards=1&include_ext_alt_text=true&include_quote_count=true&" \
                   "include_reply_count=1&tweet_mode=extended&include_entities=true&" \
                   "include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&" \
                   f"send_error_codes=true&simple_quoted_tweet=true&" \
                   f"q={words_string}{hashtags_string}{min_favs_string}until%3A{until_date}%20since%3A{from_date}" \
                   f"&count=1000&query_source=typed_query&pc=1&spelling_corrections=1&" \
                   "ext=mediaStats%2ChighlightedLabel"

    host = "https://twitter.com/i/api/2/search/adaptive.json?"

    url = host + query_string

    retries = 0
    while True:
        try:
            r = requests.get(url, headers=headers)
            break
        except ConnectionError:
            retries += 1
            if retries > 2:
                raise Exception(f'Too many retries. {from_date}')

    return r.json()


if __name__ == "__main__":

    from_date = '2014-03-01'
    until_date = '2014-03-02'

    words = ['bitcoin', 'btc']

    hashtags = ['cryptocurrency', 'btc', 'bitcoin']

    response = get_tweets(words, hashtags, from_date, until_date)




