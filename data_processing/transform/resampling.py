import numpy as np
import pandas as pd


def generate_volumebars(df, frequency=1E8):

    columns = ["open", "close", "high", "low", "volume"]

    times = df.index
    opens = df.loc[:, 'open']
    closes = df.loc[:, 'close']
    highs = df.loc[:, 'high']
    lows = df.loc[:, 'low']
    volumes = df.loc[:, 'volume']

    ans = np.zeros(shape=(len(df), 5))
    candle_counter = 0
    time_index = []

    vol = 0
    last_i = 0

    for i in range(len(df)):
        vol += volumes[i]
        if vol >= frequency:
            time_index.append(times[last_i])              # time
            ans[candle_counter, 0] = opens[last_i]                     # open
            ans[candle_counter, 1] = closes[i]                         # close
            ans[candle_counter, 2] = np.max(highs[last_i:i+1])         # high
            ans[candle_counter, 3] = np.min(lows[last_i:i+1])          # low
            ans[candle_counter, 4] = np.sum(volumes[last_i:i+1])        # volume

            candle_counter += 1
            last_i = i + 1
            vol = 0

    return pd.DataFrame(ans[:candle_counter], index=pd.DatetimeIndex(time_index), columns=columns)
