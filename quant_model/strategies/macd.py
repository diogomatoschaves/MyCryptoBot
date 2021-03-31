import numpy as np
import pandas as pd
from ta.trend import MACD as MACD_TA


class MACD(MACD_TA):
    """ Class for the vectorized backtesting of SMA-based trading strategies.
    """

    def __init__(self, window_slow, window_fast, window_signal, **kwargs):
        self.data = None

        MACD_TA.__init__(self, pd.Series(), window_slow, window_fast, window_signal)

        self.symbol = None
        self.price_col = 'close'
        self._close = pd.Series()

    def __repr__(self):
        return "{}(symbol = {}, fast = {}, slow = {}, signal = {})".format(
            self.__class__.__name__, self.symbol, self._window_fast, self._window_slow, self._window_sign
        )

    def update_data(self, data):
        """ Retrieves and prepares the data.
        """
        self._close = data[self.price_col]
        self._run()

        data["macd_diff"] = self.macd_diff()

        return data

    def _set_parameters(self, params=None):
        """ Updates SMA parameters and resp. time series.
        """

        if params is None:
            return

        if not isinstance(params, (tuple, list, type(np.array([])))):
            print(f"Invalid Parameters: {params}")
            return

        window_slow, window_fast, window_signal = params

        self._window_slow = window_slow
        self._window_fast = window_fast
        self._window_sign = window_signal

        if window_fast is not None:
            self._window_fast = window_fast
        if window_slow is not None:
            self._window_slow = window_slow
        if window_signal is not None:
            self._window_sign = window_signal

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):
        data["position"] = np.where(data["macd_diff"] > 0, 1, -1)

        return data

    def get_signal(self, row):
        if row["macd_diff"] > 0:
            return 1
        elif row["macd_diff"] < 0:
            return -1
