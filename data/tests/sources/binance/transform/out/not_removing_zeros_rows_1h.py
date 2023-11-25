from pandas import Timestamp


data = [
    {
        "open_time": Timestamp("2023-09-01 14:00:00+0000", tz="UTC"),
        "close_time": Timestamp("2023-09-01 14:59:59.999000+0000", tz="UTC"),
        "open": 55306.46,
        "high": 56333.0,
        "low": 55217.22,
        "close": 56182.11,
        "volume": 3771.962815,
        "quote_volume": 225874318.61192966,
        "trades": 98009,
        "taker_buy_asset_volume": 2202.358913,
        "taker_buy_quote_volume": 122870996.88248184,
        "exchange_id": "binance",
        "symbol_id": "BTCUSDT",
        "interval": "1h",
    },
    {
        "open_time": Timestamp("2023-09-01 15:00:00+0000", tz="UTC"),
        "close_time": Timestamp("2023-09-01 15:04:59.999000+0000", tz="UTC"),
        "open": 56182.12,
        "high": 56299.78,
        "low": 56172.09,
        "close": 56289.89,
        "volume": 298.797415,
        "quote_volume": 16804824.55255641,
        "trades": 9000,
        "taker_buy_asset_volume": 139.83665,
        "taker_buy_quote_volume": 7864202.02549528,
        "exchange_id": "binance",
        "symbol_id": "BTCUSDT",
        "interval": "1h",
    },
]

expected_value = data
