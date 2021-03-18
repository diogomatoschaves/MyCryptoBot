import numpy as np
import matplotlib.pyplot as plt


class IterativeBacktester:

    def __init__(self, data, amount, symbol='BTCUSDT', trading_costs=0, price_col='close', returns_col='returns'):
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

    def _assess_strategy(self, data, title, plot_results=True):

        data = self._calculate_position(data.copy())

        data["trades"] = data.position.diff().fillna(0).abs()

        data["strategy"] = data.position.shift(1) * data.returns
        data["strategy_tc"] = data["strategy"] - np.abs(data[self.returns_col]) * data.trades * self.tc

        data.dropna(inplace=True)

        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)
        data["creturns"] = data["returns"].cumsum().apply(np.exp)
        data["cstrategy_tc"] = data["strategy_tc"].cumsum().apply(np.exp)

        number_trades = self.trades

        print(f"Numer of trades: {number_trades}")

        self.results = data

        # absolute performance of the strategy
        perf = data["cstrategy"].iloc[-1]

        # out-/underperformance of strategy
        outperf = perf - data["creturns"].iloc[-1]

        if plot_results:
            self.plot_results(title)

        return round(perf, 6), round(outperf, 6)

    def get_values(self, data, bar):
        price = data.iloc[bar][self.price_col]
        date = data.index[bar].date()

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
            self.buy_instrument(date, price, units=-self.units) # if short position, go neutral first
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

    def plot_results(self, title):
        """ Plots the cumulative performance of the trading strategy
        compared to buy and hold.
        """
        if self.results is None:
            print("No results to plot yet. Run a strategy first.")
        else:
            plotting_cols = ["creturns", "cstrategy", "position"]
            if self.tc != 0:
                plotting_cols.append("cstrategy_tc")

            self.results[plotting_cols].plot(title=title, figsize=(12, 8), secondary_y='position')
            plt.show()
