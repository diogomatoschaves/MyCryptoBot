import time

from data.extract import get_lunarcrush_data
from data.extract import get_session_key

key = get_session_key()

symbol = 'btc'

results = []

i = 0
while True:

    i += 1
    print(i)

    result = get_lunarcrush_data(symbol, key, data_points=10, endpoint_option=5)

    results.append(result)

    if i >= 50:
        break

    time.sleep(60)
