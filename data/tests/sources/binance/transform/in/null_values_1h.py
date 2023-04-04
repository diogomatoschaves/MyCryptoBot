import shared.exchanges.binance.constants as const

import pandas as pd

from data.tests.setup.test_data.sample_data import processed_historical_data_1h

data = pd.DataFrame(processed_historical_data_1h)

data = data.drop([1, 2])

candle_size = '1h'
exchange = 'binance'
symbol = 'BTCUSDT'
aggregation_method = const.COLUMNS_AGGREGATION
is_removing_zeros = False
is_removing_rows = False
