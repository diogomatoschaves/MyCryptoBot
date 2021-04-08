headers = {
    'authority': 'api.santiment.net',
    'method': 'POST',
    'path': '/graphql',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,pt;q=0.8,es;q=0.7',
    'cache-control': 'no-cache',
    'origin': 'https://app.santiment.net',
    'pragma': 'no-cache',
    'referer': 'https://app.santiment.net/',
    'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/88.0.4324.192 Safari/537.36',
}

query = 'query getMetric($from: DateTime!, $to: DateTime!, $slug: String, $slugs: [String], $interval: interval, ' \
        '$transform: TimeseriesMetricTransformInputObject, $holdersCount: Int, $market_segments: [String], ' \
        '$ignored_slugs: [String], $source: String, $owner: String, $label: String) {\n  getMetric(metric: ' \
        '\"active_addresses_1h\") {\n    timeseriesData(selector: {slug: $slug, slugs: $slugs, holdersCount: ' \
        '$holdersCount, market_segments: $market_segments, ignored_slugs: $ignored_slugs, source: $source, ' \
        'owner: $owner, label: $label}, from: $from, to: $to, interval: $interval, transform: $transform) {\n      ' \
        'datetime\n      active_addresses_1h: value\n      __typename\n    }\n    __typename\n  }\n}\n '
