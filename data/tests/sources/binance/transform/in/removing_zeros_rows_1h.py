import shared.exchanges.binance.constants as const

import pandas as pd

from data.tests.helpers.sample_data import processed_historical_data

data = pd.DataFrame(processed_historical_data).set_index('open_time')

data.iloc[1, data.columns.get_loc("volume")] = 0
data.iloc[3, data.columns.get_loc("trades")] = 0

candle_size = '1h'
exchange = 'binance'
symbol = 'BTCUSDT'
columns_aggregation = const.COLUMNS_AGGREGATION
is_removing_zeros = True
is_removing_rows = True
