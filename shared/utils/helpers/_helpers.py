
def convert_signal_to_text(signal):
    if signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    else:
        return "NEUTRAL"


def get_logging_row_header(symbol, strategy, params, candle_size, exchange):
    return f"{symbol}|{strategy}|{params}|{candle_size}|{exchange}: "


def get_item_from_cache(cache, key):

    item = cache.get(f"pipeline {key}")

    cache.set("dict", "1234")
    print(cache.get("dict"))

    print(item)

    return item if item else '""'
