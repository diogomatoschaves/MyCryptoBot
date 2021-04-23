from model.backtesting._mixin import BacktestMixin
from shared.trading import Trader


class IterativeBacktester(BacktestMixin, Trader):

    def __init__(self, strategy, amount=1000, symbol='BTCUSDT', trading_costs=0):
        BacktestMixin.__init__(self, symbol, trading_costs)
        Trader.__init__(self, amount)

        self.strategy = strategy
        self.positions_lst = []
        self.positions = {
            symbol: 0
        }

    def __repr__(self):
        return self.strategy.__repr__()

    def __getattr__(self, attr):
        method = getattr(self.strategy, attr)

        if not method:
            return getattr(self, attr)
        else:
            return method

    def _set_position(self, symbol, value):
        self.positions[symbol] = value

    def _get_position(self, symbol):
        return self.positions[symbol]

    def _reset_object(self):
        # reset
        self._set_position(self.symbol, 0)  # initial neutral position
        self.positions_lst = []
        self.trades = 0  # no trades yet
        self.current_balance = self.initial_balance  # reset initial capital

    def _calculate_positions(self, data):
        data["position"] = self.positions_lst
        return data

    def _get_trades(self, _):
        return self.trades

    def get_values(self, _, row):
        price = row[self.price_col]

        return price

    def test_strategy(self, params=None, plot_results=True):
        """ Test a mean-reversion strategy (bollinger) with SMA and dev.
        """

        self.set_parameters(params)
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

            signal = self.get_signal(row)

            if bar != data.shape[0] - 1:
                self.trade(self.symbol, signal, timestamp, row, amount="all")
            else:
                self.close_pos(self.symbol, timestamp, row)  # close position at the last bar
                self._set_position(self.symbol, 0)

            self.positions_lst.append(self._get_position(self.symbol))

    def buy_instrument(self, symbol, date=None, row=None, units=None, amount=None):

        price = self.get_values(date, row)

        price = price * (1 + self.tc)

        if units is None:
            units = amount / price

        self.current_balance -= units * price
        self.units += units
        self.trades += 1
        print(f"{date} |  Buying {round(units, 4)} {self.symbol} for {round(price, 5)}")

    def sell_instrument(self, symbol, date=None, row=None, units=None, amount=None):

        price = self.get_values(date, row)

        price = price * (1 - self.tc)

        if units is None:
            units = amount / price

        self.current_balance += units * price
        self.units -= units
        self.trades += 1
        print(f"{date} |  Selling {round(units, 4)} {self.symbol} for {round(price, 5)}")

    def close_pos(self, symbol, date=None, row=None):

        print(75 * "-")
        print("{} |  +++ CLOSING FINAL POSITION +++".format(date))

        if self.units <= 0:
            self.buy_instrument(symbol, date, row, units=-self.units)
        else:
            self.sell_instrument(symbol, date, row, units=self.units)

        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        self.print_current_balance(symbol, date)

        print("{} |  net performance (%) = {}".format(date, round(perf, 2)))
        print("{} |  number of trades executed = {}".format(date, self.trades))
        print(75 * "-")

    def plot_data(self, cols=None):
        if cols is None:
            cols = "close"
        self.data[cols].plot(figsize=(12, 8), title='BTC/USD')
