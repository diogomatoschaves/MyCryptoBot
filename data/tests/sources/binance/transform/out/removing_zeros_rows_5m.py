import pandas as pd

data = {
    pd.Timestamp('2021-04-14 10:25:00+0000', tz='UTC'): {
        'close_time': pd.Timestamp('2021-04-14 10:29:59.999000+0000', tz='UTC'), 
        'open': 63833.07, 
        'high': 63851.97, 
        'low': 63720.15, 
        'close': 63812.53, 
        'volume': 262.674664, 
        'quote_volume': 16757728.11468282, 
        'trades': 8357.0, 
        'taker_buy_asset_volume': 133.210727, 
        'taker_buy_quote_volume': 8498600.19321323, 
        'exchange_id': 'binance', 
        'symbol_id': 'BTCUSDT', 
        'interval': '5m'
    }, 
    pd.Timestamp('2021-04-14 10:35:00+0000', tz='UTC'): {
        'close_time': pd.Timestamp('2021-04-14 10:39:59.999000+0000', tz='UTC'), 
        'open': 63843.47, 
        'high': 63990.0, 
        'low': 63843.47, 
        'close': 63958.73, 
        'volume': 340.691666, 
        'quote_volume': 21770240.49044303, 
        'trades': 7277.0, 
        'taker_buy_asset_volume': 240.874768, 
        'taker_buy_quote_volume': 15391773.69130644, 
        'exchange_id': 'binance', 
        'symbol_id': 'BTCUSDT', 
        'interval': '5m'
    }, 
    pd.Timestamp('2021-04-14 10:45:00+0000', tz='UTC'): {
        'close_time': pd.Timestamp('2021-04-14 10:49:59.999000+0000', tz='UTC'), 
        'open': 64071.4, 
        'high': 64086.37, 
        'low': 63950.0, 
        'close': 64029.98, 
        'volume': 242.394657, 
        'quote_volume': 15520898.12027384, 
        'trades': 8019.0, 
        'taker_buy_asset_volume': 114.952666, 
        'taker_buy_quote_volume': 7360749.46230163, 
        'exchange_id': 'binance', 
        'symbol_id': 'BTCUSDT', 
        'interval': '5m'
    }, 
    pd.Timestamp('2021-04-14 10:50:00+0000', tz='UTC'): {
        'close_time': pd.Timestamp('2021-04-14 10:54:59.999000+0000', tz='UTC'), 
        'open': 64029.98, 
        'high': 64143.34, 
        'low': 63961.17, 
        'close': 64096.47, 
        'volume': 227.382501, 
        'quote_volume': 14563921.76513411, 
        'trades': 7386.0, 
        'taker_buy_asset_volume': 89.989297, 
        'taker_buy_quote_volume': 5764514.08167397, 
        'exchange_id': 'binance', 
        'symbol_id': 'BTCUSDT', 
        'interval': '5m'
    }, 
    pd.Timestamp('2021-04-14 10:55:00+0000', tz='UTC'): {
        'close_time': pd.Timestamp('2021-04-14 10:59:59.999000+0000', tz='UTC'), 
        'open': 64096.47, 
        'high': 64151.48, 
        'low': 64001.27, 
        'close': 64099.99, 
        'volume': 198.388467, 
        'quote_volume': 12710504.50091237, 
        'trades': 6947.0, 
        'taker_buy_asset_volume': 106.934585, 
        'taker_buy_quote_volume': 6851132.68242858, 
        'exchange_id': 'binance', 
        'symbol_id': 'BTCUSDT', 
        'interval': '5m'
    }, 
    pd.Timestamp('2021-04-14 11:00:00+0000', tz='UTC'): {
        'close_time': pd.Timestamp('2021-04-14 11:04:59.999000+0000', tz='UTC'), 
        'open': 64100.0, 
        'high': 64430.37, 
        'low': 64084.64, 
        'close': 64426.29, 
        'volume': 355.39578, 
        'quote_volume': 22846811.06265759, 
        'trades': 10442.0, 
        'taker_buy_asset_volume': 175.595283, 
        'taker_buy_quote_volume': 11288645.41188546, 
        'exchange_id': 'binance', 
        'symbol_id': 'BTCUSDT', 
        'interval': '5m'
    }
}

expected_value = data
