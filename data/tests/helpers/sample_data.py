from datetime import datetime

import pytz

binance_api_historical_data = [
    [1618395900000, '63833.07000000', '63851.97000000', '63720.15000000', '63812.53000000', '262.67466400', 1618396199999, '16757728.11468282', 8357, '133.21072700', '8498600.19321323', '0'],
    [1618396200000, '63812.54000000', '63867.72000000', '63773.76000000', '63843.48000000', '192.08274800', 1618396499999, '12259410.45902169', 7208, '86.66541600', '5531349.03704501', '0'],
    [1618396500000, '63843.47000000', '63990.00000000', '63843.47000000', '63958.73000000', '340.69166600', 1618396799999, '21770240.49044303', 7277, '240.87476800', '15391773.69130644', '0'],
    [1618396800000, '63958.68000000', '64151.97000000', '63942.52000000', '64071.41000000', '281.84023600', 1618397099999, '18054861.01462965', 8662, '150.73271100', '9653905.59811676', '0'],
    [1618397100000, '64071.40000000', '64086.37000000', '63950.00000000', '64029.98000000', '242.39465700', 1618397399999, '15520898.12027384', 8019, '114.95266600', '7360749.46230163', '0'],
    [1618397400000, '64029.98000000', '64143.34000000', '63961.17000000', '64096.47000000', '227.38250100', 1618397699999, '14563921.76513411', 7386, '89.98929700', '5764514.08167397', '0'],
    [1618397700000, '64096.47000000', '64151.48000000', '64001.27000000', '64099.99000000', '198.38846700', 1618397999999, '12710504.50091237', 6947, '106.93458500', '6851132.68242858', '0'],
    [1618398000000, '64100.00000000', '64430.37000000', '64084.64000000', '64426.29000000', '355.39578000', 1618398299999, '22846811.06265759', 10442, '175.59528300', '11288645.41188546', '0'],
]


processed_historical_data = [
    {
        'open_time': datetime(2021, 4, 14, 10, 25, tzinfo=pytz.utc),
        'close_time': datetime(2021, 4, 14, 10, 29, 59, 999000, tzinfo=pytz.utc),
        'open': 63833.07,
        'high': 63851.97,
        'low': 63720.15,
        'close': 63812.53,
        'volume': 262.674664,
        'quote_volume': 16757728.11468282,
        'trades': 8357,
        'taker_buy_asset_volume': 133.210727,
        'taker_buy_quote_volume': 8498600.19321323
    },
    {
        'open_time': datetime(2021, 4, 14, 10, 30, tzinfo=pytz.utc),
        'close_time': datetime(2021, 4, 14, 10, 34, 59, 999000, tzinfo=pytz.utc),
        'open': 63812.54,
        'high': 63867.72,
        'low': 63773.76,
        'close': 63843.48,
        'volume': 192.082748,
        'quote_volume': 12259410.45902169,
        'trades': 7208,
        'taker_buy_asset_volume': 86.665416,
        'taker_buy_quote_volume': 5531349.03704501
    },
    {
        'open_time': datetime(2021, 4, 14, 10, 35, tzinfo=pytz.utc),
        'close_time': datetime(2021, 4, 14, 10, 39, 59, 999000, tzinfo=pytz.utc),
        'open': 63843.47,
        'high': 63990.0,
        'low': 63843.47,
        'close': 63958.73,
        'volume': 340.691666,
        'quote_volume': 21770240.49044303,
        'trades': 7277,
        'taker_buy_asset_volume': 240.874768,
        'taker_buy_quote_volume': 15391773.69130644
    },
    {
        'open_time': datetime(2021, 4, 14, 10, 40, tzinfo=pytz.utc),
        'close_time': datetime(2021, 4, 14, 10, 44, 59, 999000, tzinfo=pytz.utc),
        'open': 63958.68,
        'high': 64151.97,
        'low': 63942.52,
        'close': 64071.41,
        'volume': 281.840236,
        'quote_volume': 18054861.01462965,
        'trades': 8662,
        'taker_buy_asset_volume': 150.732711,
        'taker_buy_quote_volume': 9653905.59811676
    },
    {
        'open_time': datetime(2021, 4, 14, 10, 45, tzinfo=pytz.utc),
        'close_time': datetime(2021, 4, 14, 10, 49, 59, 999000, tzinfo=pytz.utc),
        'open': 64071.4,
        'high': 64086.37,
        'low': 63950.0,
        'close': 64029.98,
        'volume': 242.394657,
        'quote_volume': 15520898.12027384,
        'trades': 8019,
        'taker_buy_asset_volume': 114.952666,
        'taker_buy_quote_volume': 7360749.46230163
    },
    {
        'open_time': datetime(2021, 4, 14, 10, 50, tzinfo=pytz.utc),
        'close_time': datetime(2021, 4, 14, 10, 54, 59, 999000, tzinfo=pytz.utc),
        'open': 64029.98,
        'high': 64143.34,
        'low': 63961.17,
        'close': 64096.47,
        'volume': 227.382501,
        'quote_volume': 14563921.76513411,
        'trades': 7386,
        'taker_buy_asset_volume': 89.989297,
        'taker_buy_quote_volume': 5764514.08167397},
    {
        'open_time': datetime(2021, 4, 14, 10, 55, tzinfo=pytz.utc),
        'close_time': datetime(2021, 4, 14, 10, 59, 59, 999000, tzinfo=pytz.utc),
        'open': 64096.47,
        'high': 64151.48,
        'low': 64001.27,
        'close': 64099.99,
        'volume': 198.388467,
        'quote_volume': 12710504.50091237,
        'trades': 6947,
        'taker_buy_asset_volume': 106.934585,
        'taker_buy_quote_volume': 6851132.68242858
    },
    {
        'open_time': datetime(2021, 4, 14, 11, 0, tzinfo=pytz.utc),
        'close_time': datetime(2021, 4, 14, 11, 4, 59, 999000, tzinfo=pytz.utc),
        'open': 64100.0,
        'high': 64430.37,
        'low': 64084.64,
        'close': 64426.29,
        'volume': 355.39578,
        'quote_volume': 22846811.06265759,
        'trades': 10442,
        'taker_buy_asset_volume': 175.595283,
        'taker_buy_quote_volume': 11288645.41188546
    }
]

exchange_data_1 = dict(
    exchange_id='binance',
    symbol_id='BTCUSDT',
    open_time=datetime(2019, 9, 2, 10, tzinfo=pytz.utc),
    close_time=datetime(2019, 9, 1, 11, tzinfo=pytz.utc),
    interval='1h',
    open=1,
    high=1,
    low=1,
    close=1,
    volume=1,
    quote_volume=1,
    trades=1,
    taker_buy_asset_volume=1,
    taker_buy_quote_volume=1
)

exchange_data_2 = dict(
    exchange_id='binance',
    symbol_id='BTCUSDT',
    open_time=datetime(2020, 3, 1, 10, tzinfo=pytz.utc),  # different open_time
    close_time=datetime(2020, 3, 1, 11, tzinfo=pytz.utc),  # different close_time
    interval='1h',
    open=1,
    high=1,
    low=1,
    close=1,
    volume=1,
    quote_volume=1,
    trades=1,
    taker_buy_asset_volume=1,
    taker_buy_quote_volume=1
)
