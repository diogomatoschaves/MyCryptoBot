import pandas as pd


data = {
    pd.Timestamp('2021-04-14 10:00:00+0000', tz='UTC', freq='H'): {
        'close_time': pd.Timestamp('2021-04-14 10:59:59.999000+0000', tz='UTC'),
        'open': 63833.07,
        'high': 64151.97,
        'low': 63720.15,
        'close': 64099.99,
        'volume': 1553.3721910000002,
        'quote_volume': 111637564.46509752,
        'trades': 45194,
        'taker_buy_asset_volume': 923.3601699999999,
        'taker_buy_quote_volume': 59052024.746085614,
        'exchange_id': 'binance',
        'symbol_id': 'BTCUSDT',
        'interval': '1h'
    },
    pd.Timestamp('2021-04-14 11:00:00+0000', tz='UTC', freq='H'): {
        'close_time': pd.Timestamp('2021-04-14 11:04:59.999000+0000', tz='UTC'),
        'open': 64100.0,
        'high': 64430.37,
        'low': 64084.64,
        'close': 64426.29,
        'volume': 355.39578,
        'quote_volume': 22846811.06265759,
        'trades': 10442,
        'taker_buy_asset_volume': 175.595283,
        'taker_buy_quote_volume': 11288645.41188546,
        'exchange_id': 'binance',
        'symbol_id': 'BTCUSDT',
        'interval': '1h'
    }
}

expected_value = data
