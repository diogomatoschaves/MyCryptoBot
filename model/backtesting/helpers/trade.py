from dataclasses import dataclass


@dataclass
class Trade:
    """ Class for storing information about a trade.

    Parameters
    ----------
    entry_date : datetime
        Entry date in datetime format.
    exit_date : datetime
        Exit date in datetime format.
    entry_price : float, None
        Price at which the trade was entered.
    exit_price : float, None
        Price at which the trade was exited.
    units : float, None
        Number of shares or contracts traded.
    direction : int
        Trade direction, either 1 for long or -1 for short.
    profit : float
        Trade net profit
    profit_pct : float
        Trade net profit in percentage of initial investment
    """

    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    units: float
    direction: int
    profit: float
    profit_pct: float

    def calculate_profit(self):
        self.profit = (self.entry_price - self.exit_price) * self.units * self.direction
        self.profit_pct = (self.entry_price - self.exit_price) / self.entry_price * self.direction * 100
