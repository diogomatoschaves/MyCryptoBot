from strategies.backtesting.iterative.base import IterativeBacktester
from strategies.backtesting.strategies import MomentumBase


class MomentumIterBacktester(MomentumBase, IterativeBacktester):

    def __init__(self, data, amount, window):
        MomentumBase.__init__(self)
        IterativeBacktester.__init__(self, data, amount)

        self.window = window

        self._update_data()

    def test_strategy(self, window=None, plot_results=True):
        """ Backtests the trading strategy.
        """

        self._set_parameters(window)
        self._reset_object()

        window = self.window

        # nice printout
        print("-" * 75)
        print("Testing Momentum strategy | {} | window: {}".format(self.symbol, self.window))
        print("-" * 75)

        data = self.data.dropna().copy()

        data["rolling_returns"] = data[self.returns_col].rolling(window, min_periods=1).mean()
        data.dropna(inplace=True)

        # Momentum strategy
        for bar, (timestamp, row) in enumerate(data.iloc[:-1].iterrows()):

            date, price = self.get_values(data, bar)

            if row["rolling_returns"] >= 0: # signal to go long
                if self.position in [0, -1]:
                    self.go_long(date, price, amount="all")  # go long with full amount
                    self.position = 1  # long position
            elif row["rolling_returns"] < 0:  # signal to go short
                if self.position in [0, 1]:
                    self.go_short(date, price, amount="all")  # go short with full amount
                    self.position = -1  # short position

            self.positions.append(self.position)

        self.close_pos(data, bar + 1)  # close position at the last bar

        self.positions.append(0)

        title = self.__repr__()

        return self._assess_strategy(data, title, plot_results)
