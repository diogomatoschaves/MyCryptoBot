from datetime import datetime

import pytz

BINANCE_API_KEY = "BINANCE_API_KEY"
BINANCE_API_SECRET = "BINANCE_API_SECRET"

BINANCE_API_KEY_TEST = "BINANCE_API_KEY_TEST"
BINANCE_API_SECRET_TEST = "BINANCE_API_SECRET_TEST"

BINANCE_SPOT_TRADING = "SPOT"
BINANCE_MARGIN_TRADING = "MARGIN"

CANDLE_SIZES_MAPPER = {
    '1m': '1T',
    '5m': '5T',
    '10m': '10T',
    '15m': '15T',
    '30m': '30T',
    '1h': '1H',
    '1d': '1D',
}

COUNT_MAPPER = {
    '5m': 1,
    '10m': 2,
    '15m': 3,
    '30m': 6,
    '1h': 12,
    '1d': 288,
}

COLUMNS_AGGREGATION = {
    "close_time": 'last',
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": 'sum',
    "quote_volume": "sum",
    "trades": "sum",
    "taker_buy_asset_volume": "sum",
    "taker_buy_quote_volume": "sum"
}

COLUMNS_AGGREGATION_WEBSOCKET = {
    "close_time": 'last',
    "open": "last",
    "high": "last",
    "low": "last",
    "close": "last",
    "volume": 'last',
    "quote_volume": "last",
    "trades": "last",
    "taker_buy_asset_volume": "last",
    "taker_buy_quote_volume": "last"
}

NAME_MAPPER = {
    "t": "open_time",
    "T": "close_time",
    "o": "open",
    "c": "close",
    "h": "high",
    "l": "low",
    "v": "volume",
    "n": "trades",
    "q": "quote_volume",
    "V": "taker_buy_asset_volume",
    "Q": "taker_buy_quote_volume",
}

FUNCTION_MAPPER = {
    "t": lambda x: datetime.fromtimestamp(x / 1000).astimezone(pytz.utc),
    "T": lambda x: datetime.fromtimestamp(x / 1000).astimezone(pytz.utc),
    "o": lambda x: float(x),
    "c": lambda x: float(x),
    "h": lambda x: float(x),
    "l": lambda x: float(x),
    "v": lambda x: float(x),
    "n": lambda x: float(x),
    "q": lambda x: float(x),
    "V": lambda x: float(x),
    "Q": lambda x: float(x),
}


BINANCE_KEY = {
    "open_time": lambda x: datetime.fromtimestamp(x[0] / 1000).astimezone(pytz.timezone('UTC')),
    "close_time": lambda x: datetime.fromtimestamp(x[6] / 1000).astimezone(pytz.timezone('UTC')),
    "open": lambda x: float(x[1]),
    "high": lambda x: float(x[2]),
    "low": lambda x: float(x[3]),
    "close": lambda x: float(x[4]),
    "volume": lambda x: float(x[5]),
    "quote_volume": lambda x: float(x[7]),
    "trades": lambda x: int(x[8]),
    "taker_buy_asset_volume": lambda x: float(x[9]),
    "taker_buy_quote_volume": lambda x: float(x[10]),
}