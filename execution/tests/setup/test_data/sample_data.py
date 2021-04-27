from datetime import datetime

import pytz
from pandas import Timestamp


binance_api_historical_data = [
    [1619013600000, '55306.46000000', '55399.68000000', '55217.22000000', '55388.96000000', '276.69073400', 1619013599999, '15295597.50785806', 7614, '145.21142400', '8027028.99029815', '0'],
    [1619013900000, '55306.46000000', '55399.68000000', '55217.22000000', '55388.96000000', '276.69073400', 1619013899999, '15295597.50785806', 7614, '145.21142400', '8027028.99029815', '0'],
    [1619014200000, '55306.46000000', '55399.68000000', '55217.22000000', '55388.96000000', '276.69073400', 1619014199999, '15295597.50785806', 7614, '145.21142400', '8027028.99029815', '0'],
    [1619014500000, '55306.46000000', '55399.68000000', '55217.22000000', '55388.96000000', '276.69073400', 1619014499999, '15295597.50785806', 7614, '145.21142400', '8027028.99029815', '0'],
    [1619014800000, '55306.46000000', '55399.68000000', '55217.22000000', '55388.96000000', '276.69073400', 1619014799999, '15295597.50785806', 7614, '145.21142400', '8027028.99029815', '0'],
    [1619015100000, '55388.95000000', '55569.95000000', '55388.95000000', '55552.40000000', '149.36342600', 1619015399999, '8288967.03877351', 5260, '82.67909000', '4588065.23181743', '0'],
    [1619015400000, '55550.89000000', '56087.68000000', '55550.89000000', '55932.48000000', '692.92431900', 1619015699999, '38726480.58078431', 16507, '411.22301700', '22979821.33981915', '0'],
    [1619015700000, '55932.48000000', '56333.00000000', '55932.48000000', '56264.93000000', '603.66011800', 1619015999999, '33896505.69714660', 14656, '356.91588300', '20037884.70780964', '0'],
    [1619016000000, '56260.11000000', '56317.43000000', '56118.31000000', '56168.82000000', '370.50035900', 1619016299999, '20822485.25288953', 8616, '178.07590400', '10007121.78892216', '0'],
    [1619016300000, '56168.82000000', '56269.99000000', '56080.96000000', '56191.11000000', '324.51432000', 1619016599999, '18225087.41727558', 8352, '145.06438100', '8146012.47892439', '0'],
    [1619016600000, '56191.11000000', '56200.00000000', '56107.98000000', '56145.00000000', '254.09160600', 1619016899999, '14265787.89818125', 6455, '134.11240000', '7529521.30623853', '0'],
    [1619016900000, '56145.00000000', '56211.70000000', '56106.97000000', '56182.11000000', '270.14573100', 1619017199999, '15171017.18758856', 7707, '168.23111800', '9447425.07745980', '0'],
    [1619017200000, '56182.12000000', '56299.78000000', '56172.09000000', '56289.89000000', '298.79741500', 1619017499999, '16804824.55255641', 9000, '139.83665000', '7864202.02549528', '0']
]


processed_historical_data = [
    {
        'open_time': Timestamp('2021-04-21 14:00:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 13:59:59.999000+0000', tz='UTC'),
        'open': 55306.46,
        'high': 55399.68,
        'low': 55217.22,
        'close': 55388.96,
        'volume': 276.690734,
        'quote_volume': 15295597.50785806,
        'trades': 7614,
        'taker_buy_asset_volume': 145.211424,
        'taker_buy_quote_volume': 8027028.99029815
    },
    {
        'open_time': Timestamp('2021-04-21 14:05:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:04:59.999000+0000', tz='UTC'),
        'open': 55306.46,
        'high': 55399.68,
        'low': 55217.22,
        'close': 55388.96,
        'volume': 276.690734,
        'quote_volume': 15295597.50785806,
        'trades': 7614,
        'taker_buy_asset_volume': 145.211424,
        'taker_buy_quote_volume': 8027028.99029815
    },
    {
        'open_time': Timestamp('2021-04-21 14:10:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:09:59.999000+0000', tz='UTC'),
        'open': 55306.46,
        'high': 55399.68,
        'low': 55217.22,
        'close': 55388.96,
        'volume': 276.690734,
        'quote_volume': 15295597.50785806,
        'trades': 7614,
        'taker_buy_asset_volume': 145.211424,
        'taker_buy_quote_volume': 8027028.99029815
    },
    {
        'open_time': Timestamp('2021-04-21 14:15:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:14:59.999000+0000', tz='UTC'),
        'open': 55306.46,
        'high': 55399.68,
        'low': 55217.22,
        'close': 55388.96,
        'volume': 276.690734,
        'quote_volume': 15295597.50785806,
        'trades': 7614,
        'taker_buy_asset_volume': 145.211424,
        'taker_buy_quote_volume': 8027028.99029815
    },
    {
        'open_time': Timestamp('2021-04-21 14:20:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:19:59.999000+0000', tz='UTC'),
        'open': 55306.46,
        'high': 55399.68,
        'low': 55217.22,
        'close': 55388.96,
        'volume': 276.690734,
        'quote_volume': 15295597.50785806,
        'trades': 7614,
        'taker_buy_asset_volume': 145.211424,
        'taker_buy_quote_volume': 8027028.99029815
    },
    {
        'open_time': Timestamp('2021-04-21 14:25:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:29:59.999000+0000', tz='UTC'),
        'open': 55388.95,
        'high': 55569.95,
        'low': 55388.95,
        'close': 55552.4,
        'volume': 149.363426,
        'quote_volume': 8288967.03877351,
        'trades': 5260,
        'taker_buy_asset_volume': 82.67909,
        'taker_buy_quote_volume': 4588065.23181743
    },
    {
        'open_time': Timestamp('2021-04-21 14:30:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:34:59.999000+0000', tz='UTC'),
        'open': 55550.89,
        'high': 56087.68,
        'low': 55550.89,
        'close': 55932.48,
        'volume': 692.924319,
        'quote_volume': 38726480.58078431,
        'trades': 16507,
        'taker_buy_asset_volume': 411.223017,
        'taker_buy_quote_volume': 22979821.33981915
    },
    {
        'open_time': Timestamp('2021-04-21 14:35:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:39:59.999000+0000', tz='UTC'),
        'open': 55932.48,
        'high': 56333.0,
        'low': 55932.48,
        'close': 56264.93,
        'volume': 603.660118,
        'quote_volume': 33896505.6971466,
        'trades': 14656,
        'taker_buy_asset_volume': 356.915883,
        'taker_buy_quote_volume': 20037884.70780964
    },
    {
        'open_time': Timestamp('2021-04-21 14:40:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:44:59.999000+0000', tz='UTC'),
        'open': 56260.11,
        'high': 56317.43,
        'low': 56118.31,
        'close': 56168.82,
        'volume': 370.500359,
        'quote_volume': 20822485.25288953,
        'trades': 8616,
        'taker_buy_asset_volume': 178.075904,
        'taker_buy_quote_volume': 10007121.78892216
    },
    {
        'open_time': Timestamp('2021-04-21 14:45:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:49:59.999000+0000', tz='UTC'),
        'open': 56168.82,
        'high': 56269.99,
        'low': 56080.96,
        'close': 56191.11,
        'volume': 324.51432,
        'quote_volume': 18225087.41727558,
        'trades': 8352,
        'taker_buy_asset_volume': 145.064381,
        'taker_buy_quote_volume': 8146012.47892439
    },
    {
        'open_time': Timestamp('2021-04-21 14:50:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:54:59.999000+0000', tz='UTC'),
        'open': 56191.11,
        'high': 56200.0,
        'low': 56107.98,
        'close': 56145.0,
        'volume': 254.091606,
        'quote_volume': 14265787.89818125,
        'trades': 6455,
        'taker_buy_asset_volume': 134.1124,
        'taker_buy_quote_volume': 7529521.30623853
    },
    {
        'open_time': Timestamp('2021-04-21 14:55:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 14:59:59.999000+0000', tz='UTC'),
        'open': 56145.0,
        'high': 56211.7,
        'low': 56106.97,
        'close': 56182.11,
        'volume': 270.145731,
        'quote_volume': 15171017.18758856,
        'trades': 7707,
        'taker_buy_asset_volume': 168.231118,
        'taker_buy_quote_volume': 9447425.0774598
    },
    {
        'open_time': Timestamp('2021-04-21 15:00:00+0000', tz='UTC'),
        'close_time': Timestamp('2021-04-21 15:04:59.999000+0000', tz='UTC'),
        'open': 56182.12,
        'high': 56299.78,
        'low': 56172.09,
        'close': 56289.89,
        'volume': 298.797415,
        'quote_volume': 16804824.55255641,
        'trades': 9000,
        'taker_buy_asset_volume': 139.83665,
        'taker_buy_quote_volume': 7864202.02549528
    }]


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

mock_websocket_raw_data_1h = [
    {
        'stream': 'btcusdt@kline_1h',
        'data': {
            'e': 'kline',
            'E': 1619016481474,
            's': 'BTCUSDT',
            'k': {
                't': 1619013600000,
                'T': 1619017199999,
                's': 'BTCUSDT',
                'i': '1h',
                'f': 782581734,
                'L': 782663832,
                'o': '55569.31000000',
                'c': '56096.40000000',
                'h': '56333.00000000',
                'l': '55217.22000000',
                'v': '3075.65572200',
                'n': 82099,
                'x': False,
                'q': '171652587.55776661',
                'V': '1631.69707600',
                'Q': '91069372.32011878',
                'B': '0'
            }
        }
    },
    {
        'stream': 'btcusdt@kline_1h',
        'data': {
            'e': 'kline',
            'E': 1619016481474,
            's': 'BTCUSDT',
            'k': {
                't': 1619017200000,
                'T': 1619020799999,
                's': 'BTCUSDT',
                'i': '1h',
                'f': 782581734,
                'L': 782663832,
                'o': '55569.31000000',
                'c': '56096.40000000',
                'h': '56333.00000000',
                'l': '55217.22000000',
                'v': '3075.65572200',
                'n': 82099,
                'x': False,
                'q': '171652587.55776661',
                'V': '1631.69707600',
                'Q': '91069372.32011878',
                'B': '0'
            }
        }
    }
]


mock_websocket_raw_data_5m = [
    {
        'stream': 'btcusdt@kline_5m',
        'data': {
            'e': 'kline',
            'E': 1618569347477,
            's': 'BTCUSDT',
            'k': {
                't': 1618569300000,
                'T': 1618569599999,
                's': 'BTCUSDT',
                'i': '5m',
                'f': 769635350,
                'L': 769637787,
                'o': '60620.95000000',
                'c': '60538.28000000',
                'h': '60661.64000000',
                'l': '60500.00000000',
                'v': '97.41278900',
                'n': 2438,
                'x': False,
                'q': '5900443.49938099',
                'V': '44.97156100',
                'Q': '2724454.34160373',
                'B': '0'
            }
        }
    },
    {
        'stream': 'btcusdt@kline_5m',
        'data': {
            'e': 'kline',
            'E': 1618569347477,
            's': 'BTCUSDT',
            'k': {
                't': 1618569600000,
                'T': 1618569899999,
                's': 'BTCUSDT',
                'i': '5m',
                'f': 769635350,
                'L': 769637787,
                'o': '60620.95000000',
                'c': '60538.28000000',
                'h': '60661.64000000',
                'l': '60500.00000000',
                'v': '97.41278900',
                'n': 2438,
                'x': False,
                'q': '5900443.49938099',
                'V': '44.97156100',
                'Q': '2724454.34160373',
                'B': '0'
            }
        }
    },
]
