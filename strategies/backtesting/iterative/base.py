import numpy as np

from strategies.backtesting.base import BacktestBase
from trading_automation.trading import Trader


class IterativeBacktester(BacktestBase, Trader):

    def __init__(self, data, amount, symbol='BTCUSDT', trading_costs=0, price_col='close', returns_col='returns'):
        BacktestBase.__init__(self)
        Trader.__init__(self, amount)

        self.data = data.copy()
        self.results = None

        self.symbol = symbol

        self.price_col = price_col
        self.returns_col = returns_col
        self.tc = trading_costs / 100
        
        self.positions = []

        self._calculate_returns()

    def _calculate_returns(self):
        self.data[self.returns_col] = np.log(self.data[self.price_col] / self.data[self.price_col].shift(1))

    def _update_data(self):
        """ Retrieves and prepares the data.
        """
        raise NotImplementedError

    def _reset_object(self):
        # reset
        self.position = 0  # initial neutral position
        self.positions = []
        self.trades = 0  # no trades yet
        self.current_balance = self.initial_balance  # reset initial capital
        self._update_data()  # reset dataset
        
    def _calculate_positions(self, data):
        data["position"] = self.positions
        return data

    def _get_signal(self, row):
        raise NotImplementedError

    def _get_trades(self, data):
        return self.trades

    def get_values(self, date, row):
        price = row[self.price_col]

        return price

    def _get_test_title(self):
        raise NotImplementedError

    def _get_data(self):
        return self.data

    def test_strategy(self, params=None, plot_results=True):
        """ Test a mean-reversion strategy (bollinger) with SMA and dev.
        """

        self._set_parameters(params)
        self._reset_object()

        # nice printout
        print("-" * 75)
        print(self._get_test_title())
        print("-" * 75)

        data = self._get_data().dropna().copy()

        self.iterative_backtest(data)

        title = self.__repr__()

        return self._assess_strategy(data, title, plot_results)

    def iterative_backtest(self, data):

        for bar, (timestamp, row) in enumerate(data.iterrows()):

            signal = self._get_signal(row)

            if bar != data.shape[0] - 1:
                self.trade(signal, timestamp, row, amount="all")
            else:
                self.close_pos(timestamp, row)  # close position at the last bar
                self.position = 0

            self.positions.append(self.position)

    def buy_instrument(self, date, row, units=None, amount=None):

        price = self.get_values(date, row)

        price = price * (1 + self.tc)

        if units is None:
            units = amount / price

        self.current_balance -= units * price
        self.units += units
        self.trades += 1
        print(f"{date} |  Buying {round(units, 4)} {self.symbol} for {round(price, 5)}")

    def sell_instrument(self, date, row, units=None, amount=None):

        price = self.get_values(date, row)

        price = price * (1 - self.tc)

        if units is None:
            units = amount / price

        self.current_balance += units * price
        self.units -= units
        self.trades += 1
        print(f"{date} |  Selling {round(units, 4)} {self.symbol} for {round(price, 5)}")

    def close_pos(self, date, row):

        print(75 * "-")
        print("{} |  +++ CLOSING FINAL POSITION +++".format(date))

        if self.units <= 0:
            self.buy_instrument(date, row, units=-self.units)
        else:
            self.sell_instrument(date, row, units=self.units)

        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        self.print_current_balance(date)

        print("{} |  net performance (%) = {}".format(date, round(perf, 2) ))
        print("{} |  number of trades executed = {}".format(date, self.trades))
        print(75 * "-")

    def print_current_position_value(self, date, price):
        cpv = self.units * price
        print(f"{date} |  Current Position Value = {round(cpv, 2)}")

    def print_current_nav(self, date, price):
        nav = self.current_balance + self.units * price
        print(f"{date} |  Net Asset Value = {round(nav, 2)}")

    def print_current_balance(self, date):
        print("{} |  Current Balance: {}".format(date, round(self.current_balance, 2)))

    def plot_data(self, cols = None):
        if cols is None:
            cols = "close"
        self.data[cols].plot(figsize=(12, 8), title='BTC/USD')