def get_twitter_headers():

    request_headers = {
        "authority": "twitter.com",
        "method": "GET",
        "path": "/i/api/2/search/adaptive.json?include_profile_interstitial_type=1&include_blocking=1&"
                "include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&"
                "include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12&include_cards=1&"
                "include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&"
                "include_entities=true&include_user_entities=true&include_ext_media_color=true&"
                "include_ext_media_availability=true&send_error_codes=true&simple_quoted_tweet=true&"
                "q=ripple%20(%23cryptocurrency)%20since%3A2007-03-03&count=20&query_source=typed_query&"
                "pc=1&spelling_corrections=1&ext=mediaStats%2ChighlightedLabel",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,pt;q=0.8,es;q=0.7",
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puT"
                         "s%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "cookie": "personalization_id='1_VfXEw0HmHHXbPLT2hyynVw=='; syndication_guest_id=v1%3A158455737144301849; "
                  "guest_id=v1%3A158455737258319383; at_check=true; _ga=GA1.2.1365352928.1613132439; "
                  "_gid=GA1.2.1259082982.1613132439; des_opt_in=Y; eu_cn=1; gt=1360204206595059717; "
                  "external_referer=padhuUp37zixoA2Yz6IlsoQTSjz5FgRcKMoWWYN3PEQ%3D|0|8e8t2xd8A2w%3D; "
                  "ads_prefs='HBERAAA='; kdt=fsLzrgUxYX5L94UUIUyaBiFFGAqeJoQwKan9RTGJ; remember_checked_on=1; "
                  "_twitter_sess=BAh7CiIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsAB"
                  "joKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCD0XN5Z3AToMY3NyZl9p%250AZCIlZDdmNDc3NzhkZjc4YWY3NjE3NGEx"
                  "ZjJhMjcxMTRlOGU6B2lkIiVlYzcy%250ANTQwNTAxZmNiZGUyZmMzM2FjZmNkOTMzMTZlMzoJdXNlcmkE6%252Bo"
                  "BFA%253D%253D--8c2ced2a8d8f71f5d9b0e25b373d4bf57f37f1d2; auth_token=cb25fcd5188dd40988b9"
                  "c90cfcbeae31dc530e4f; ct0=c0dd8d1174fc63d2923674a4053d1e53aabd4bc69fc872389b9a653b43c0694"
                  "d6b59d4d584ba2e2520b6e633fc50a1a738b9415598d0552fc7fbf7e7abccb47e801e2b5b0ce6a1e83736d24a"
                  "7823230d; twid=u%3D335669995; mbox=session#e8b952906412456284daf1fafd89fce2#1613134298|"
                  "PC#e8b952906412456284daf1fafd89fce2.37_0#1676378421; lang=en-gb",
        "referer": "https://twitter.com/search?q=ripple%20(%23cryptocurrency)%20since%3A2007-03-03&src=typed_query",
        "sec-ch-ua": "'Google Chrome';v='87', 'Not;A Brand';v='99', 'Chromium';v='87'",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/87.0.4280.88 Safari/537.36",
        "x-csrf-token": "c0dd8d1174fc63d2923674a4053d1e53aabd4bc69fc872389b9a653b43c0694d6b59d4d584ba2e2"
                        "520b6e633fc50a1a738b9415598d0552fc7fbf7e7abccb47e801e2b5b0ce6a1e83736d24a7823230d",
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "en",
    }

    return request_headers