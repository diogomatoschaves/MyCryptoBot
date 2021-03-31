import numpy as np

from quant_model.strategies import MeanRevBase
from quant_model.backtesting.vectorized.base import VectorizedBacktester


class MeanRevVectBacktester(MeanRevBase, VectorizedBacktester):
    """ Class for the vectorized backtesting of SMA-based trading strategies.

    Attributes
    ==========
    symbol: str
        ticker symbol with which to work with
    ma: int
        time window in days for shorter SMA
    sd: int
        time window in days for longer SMA

    """

    def __init__(self, data, ma, sd, trading_costs=0, symbol='BTCUSDT'):
        MeanRevBase.__init__(self, ma, sd)
        VectorizedBacktester.__init__(self, data, trading_costs=trading_costs, symbol=symbol)

        self.data = self.update_data(self.data)

    def _calculate_positions(self, data):
        data["distance"] = data[self.price_col] - data["sma"]
        data["position"] = np.where(data[self.price_col] > data["upper"], -1, np.nan)
        data["position"] = np.where(data[self.price_col] < data["lower"], 1, data["position"])
        data["position"] = np.where(data["distance"] * data["distance"].shift(1) < 0, 0, data["position"])
        data["position"] = data["position"].ffill().fillna(0)

        return data
