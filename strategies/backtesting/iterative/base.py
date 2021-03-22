import numpy as np
import matplotlib.pyplot as plt

from strategies.backtesting.base import BacktestBase


class IterativeBacktester(BacktestBase):

    def __init__(self, data, amount, symbol='BTCUSDT', trading_costs=0, price_col='close', returns_col='returns'):
        BacktestBase.__init__(self)

        self.data = data.copy()
        self.results = None
        self.initial_balance = amount
        self.current_balance = amount
        self.units = 0
        self.trades = 0
        self.symbol = symbol

        self.price_col = price_col
        self.returns_col = returns_col
        self.tc = trading_costs / 100
        
        self.position = 0
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
        
    def _calculate_position(self, data):
        data["position"] = self.positions
        return data

    def _get_trades(self, data):
        return self.trades

    def get_values(self, data, bar):
        price = data.iloc[bar][self.price_col]

        date = data.index[bar]

        return date, price

    def buy_instrument(self, date, price, units=None, amount=None):

        price = price * (1 + self.tc)

        if units is None:
            units = amount / price

        self.current_balance -= units * price
        self.units += units
        self.trades += 1
        print(f"{date} |  Buying {round(units, 4)} {self.symbol} for {round(price, 5)}")

    def sell_instrument(self, date, price, units=None, amount=None):

        price = price * (1 - self.tc)

        if units is None:
            units = amount / price

        self.current_balance += units * price
        self.units -= units
        self.trades += 1
        print(f"{date} |  Selling {round(units, 4)} {self.symbol} for {round(price, 5)}")

    def close_pos(self, data, bar):

        date, price = self.get_values(data, bar)

        print(75 * "-")
        print("{} |  +++ CLOSING FINAL POSITION +++".format(date))

        if self.units <= 0:
            self.buy_instrument(date, price, units=-self.units)
        else:
            self.sell_instrument(date, price, units=self.units)

        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        self.print_current_balance(date)

        print("{} |  net performance (%) = {}".format(date, round(perf, 2) ))
        print("{} |  number of trades executed = {}".format(date, self.trades))
        print(75 * "-")

    # helper method
    def go_long(self, date, price, units=None, amount=None):
        if self.position == -1:
            self.buy_instrument(date, price, units=-self.units)  # if short position, go neutral first
        if units:
            self.buy_instrument(date, price, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.buy_instrument(date, price, amount=amount) # go long

    # helper method
    def go_short(self, date, price, units=None, amount=None):
        if self.position == 1:
            self.sell_instrument(date, price, units=self.units) # if long position, go neutral first
        if units:
            self.sell_instrument(date, price, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.sell_instrument(date, price, amount=amount) # go short

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
