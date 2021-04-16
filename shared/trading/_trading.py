import logging


class Trader:

    def __init__(self, amount, units=0):

        self.initial_balance = amount
        self.current_balance = amount
        self.units = units
        self.trades = 0

    def _set_position(self, symbol, value):
        raise NotImplementedError

    def _get_position(self, symbol):
        raise NotImplementedError

    def buy_instrument(self, symbol, date=None, row=None, units=None, amount=None):
        raise NotImplementedError

    def sell_instrument(self, symbol, date=None, row=None, units=None, amount=None):
        raise NotImplementedError

    def close_pos(self, symbol, date=None, row=None):
        raise NotImplementedError

    # helper method
    def go_long(self, symbol, position, date, row, units=None, amount=None):
        if position == -1:
            self.buy_instrument(symbol, date, row, units=-self.units)  # if short position, go neutral first

        if units:
            self.buy_instrument(symbol, date, row, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.buy_instrument(symbol, date, row, amount=amount)  # go long

    # helper method
    def go_short(self, symbol, position, date, row, units=None, amount=None):
        if position == 1:
            self.sell_instrument(symbol, date, row, units=self.units)  # if long position, go neutral first

        if units:
            self.sell_instrument(symbol, date, row, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.sell_instrument(symbol, date, row, amount=amount)  # go short

    def trade(self, symbol, signal, date=None, row=None, amount=None, units=None):

        position = self._get_position(symbol)

        if signal == 1:  # signal to go long
            if position in [0, -1]:
                self.go_long(symbol, position, date, row, amount=amount, units=units)  # go long with full amount
                self._set_position(symbol, 1)  # long position
        elif signal == -1:  # signal to go short
            if position in [0, 1]:
                self.go_short(symbol, position, date, row, amount=amount, units=units)  # go short with full amount
                self._set_position(symbol, -1)  # short position
        elif signal == 0:
            if position == -1:
                self.buy_instrument(symbol, date, row, units=-self.units)
            elif position == 1:
                self.sell_instrument(symbol, date, row, units=self.units)
            self._set_position(symbol, 0)

        if position == signal:
            verbose_position = "LONG" if position == 1 else "SHORT" if position == -1 else "NEUTRAL"
            logging.info(f"Maintaining {verbose_position} position.")

    def print_current_position_value(self, symbol, date, price):
        cpv = self.units * price
        print(f"{symbol}: {date} | Current Position Value = {round(cpv, 2)}")

    def print_current_nav(self, symbol, date, price):
        nav = self.current_balance + self.units * price
        print(f"{symbol}: {date} | Net Asset Value = {round(nav, 2)}")

    def print_current_balance(self, symbol, date):
        print(f"{symbol}: {date} | Current Balance: {round(self.current_balance, 2)}")
