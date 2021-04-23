from datetime import datetime

import pytz


sample_structured_data = [
    dict(
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
]
