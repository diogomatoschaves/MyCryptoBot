from strategies.backtesting.iterative.base import IterativeBacktester
from strategies.backtesting.strategies import SMABase


class SMAIterBacktester(SMABase, IterativeBacktester):

    def __init__(self, data, amount, SMA_S, SMA_L, trading_costs=0, symbol='BTCUSDT'):
        SMABase.__init__(self)
        IterativeBacktester.__init__(self, data, amount, symbol=symbol, trading_costs=trading_costs)

        self.SMA_S = SMA_S
        self.SMA_L = SMA_L

        self._update_data()

    def test_strategy(self, sma=None, plot_results=True):

        self._set_parameters(sma)
        self._reset_object()

        sma_s = self.SMA_S
        sma_l = self.SMA_L

        # nice printout
        print("-" * 75)
        print("Testing SMA strategy | {} | SMA_S = {} & SMA_L = {}".format(self.symbol, sma_s, sma_l))
        print("-" * 75)

        data = self.data.dropna().copy()

        for bar, (timestamp, row) in enumerate(data.iloc[:-1].iterrows()):

            date, price = self.get_values(data, bar)

            if row["SMA_S"] > row["SMA_L"]:
                if self.position in [0, -1]:
                    self.go_long(date, price, amount="all")
                    self.position = 1
            elif row["SMA_S"] < row["SMA_L"]:
                if self.position in [0, 1]:
                    self.go_short(date, price, amount="all")
                    self.position = -1

            self.positions.append(self.position)

        self.close_pos(data, bar + 1)

        self.positions.append(0)

        title = self.__repr__()

        return self._assess_strategy(data, title, plot_results)
