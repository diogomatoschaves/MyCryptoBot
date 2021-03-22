

class Trader:

    def __init__(self, data, amount):

        self.data = data.copy()
        self.initial_balance = amount
        self.current_balance = amount
        self.units = 0
        self.trades = 0

        self.position = 0
        self.positions = []

    def buy_instrument(self, date, row, units=None, amount=None):
        raise NotImplementedError

    def sell_instrument(self, date, row, units=None, amount=None):
        raise NotImplementedError

    def close_pos(self, data, bar):
        raise NotImplementedError

    # helper method
    def go_long(self, date, row, units=None, amount=None):
        if self.position == -1:
            self.buy_instrument(date, row, units=-self.units)  # if short position, go neutral first

        if units:
            self.buy_instrument(date, row, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.buy_instrument(date, row, amount=amount)  # go long

    # helper method
    def go_short(self, date, row, units=None, amount=None):
        if self.position == 1:
            self.sell_instrument(date, row, units=self.units)  # if long position, go neutral first

        if units:
            self.sell_instrument(date, row, units=units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.sell_instrument(date, row, amount=amount) # go short

    def trade(self, signal, date, row, amount="all"):

        if signal == 1:  # signal to go long
            if self.position in [0, -1]:
                self.go_long(date, row, amount=amount)  # go long with full amount
                self.position = 1  # long position
        elif signal == -1:  # signal to go short
            if self.position in [0, 1]:
                self.go_short(date, row, amount=amount)  # go short with full amount
                self.position = -1  # short position
        elif signal == 0:
            if self.position == -1:
                self.buy_instrument(date, row, units=-self.units)
            elif self.position == 1:
                self.sell_instrument(date, row, units=self.units)
            self.position = 0

    def print_current_position_value(self, date, price):
        cpv = self.units * price
        print(f"{date} |  Current Position Value = {round(cpv, 2)}")

    def print_current_nav(self, date, price):
        nav = self.current_balance + self.units * price
        print(f"{date} |  Net Asset Value = {round(nav, 2)}")

    def print_current_balance(self, date):
        print("{} |  Current Balance: {}".format(date, round(self.current_balance, 2)))
