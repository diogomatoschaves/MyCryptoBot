import logging


class Trader:

    def __init__(self, amount, units=0):

        self.initial_balance = amount
        self.current_balance = amount
        self.units = units
        self.trades = 0

    def _set_position(self, symbol, value, **kwargs):
        raise NotImplementedError

    def _get_position(self, symbol):
        raise NotImplementedError

    def buy_instrument(self, symbol, date=None, row=None, units=None, amount=None, header='', **kwargs):
        raise NotImplementedError

    def sell_instrument(self, symbol, date=None, row=None, units=None, amount=None, header='', **kwargs):
        raise NotImplementedError

    def close_pos(self, symbol, date=None, row=None, header='', **kwargs):
        raise NotImplementedError

    def go_long(self, symbol, position, date, row, units=None, amount=None, header='', **kwargs):
        if position == -1:
            self.buy_instrument(symbol, date, row, units=-self.units, header=header, **kwargs)  # if short position, go neutral first

        if units:
            self.buy_instrument(symbol, date, row, units=units, header=header, **kwargs)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.buy_instrument(symbol, date, row, amount=amount, header=header, **kwargs)  # go long

    # helper method
    def go_short(self, symbol, position, date, row, units=None, amount=None, header='', **kwargs):
        if position == 1:
            self.sell_instrument(symbol, date, row, units=self.units, header=header, **kwargs)  # if long position, go neutral first
        if units:
            self.sell_instrument(symbol, date, row, units=units, header=header, **kwargs)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.sell_instrument(symbol, date, row, amount=amount, header=header, **kwargs)  # go short

    def trade(self, symbol, signal, date=None, row=None, amount=None, units=None, header='', **kwargs):

        position = self._get_position(symbol)

        if signal == 1:  # signal to go long
            if position in [0, -1]:
                # go long with full amount
                self.go_long(symbol, position, date, row, amount=amount, units=units, header=header, **kwargs)
                self._set_position(symbol, 1, previous_position=position, **kwargs)  # long position
        elif signal == -1:  # signal to go short
            if position in [0, 1]:
                # go short with full amount
                self.go_short(symbol, position, date, row, amount=amount, units=units, header=header, **kwargs)
                self._set_position(symbol, -1, previous_position=position, **kwargs)  # short position
        elif signal == 0:
            if position == -1:
                self.buy_instrument(symbol, date, row, units=-self.units, header=header, **kwargs)
            elif position == 1:
                self.sell_instrument(symbol, date, row, units=self.units, header=header, **kwargs)

            self._set_position(symbol, 0, previous_position=position, **kwargs)

        if position == signal:
            verbose_position = "LONG" if position == 1 else "SHORT" if position == -1 else "NEUTRAL"

            logging.info(header + f"Maintaining {verbose_position} position.")

    def print_current_position_value(self, date, price, header=''):
        cpv = self.units * price
        print(header + f"| {date} | Current Position Value = {round(cpv, 2)}")

    def print_current_nav(self, date, price, header=''):
        nav = self.current_balance + self.units * price
        print(header + f"| {date} | Net Asset Value = {round(nav, 2)}")

    def print_current_balance(self, date, header=''):
        print(header + f"| {date} | Current Balance: {round(self.current_balance, 2)}")
