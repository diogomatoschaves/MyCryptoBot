import numpy as np

from dataclasses import dataclass
from datetime import datetime


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
    side : int
        Trade side, either 1 for long or -1 for short.
    profit : float
        Trade net profit
    """

    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    units: float
    side: int
    amount: float = None
    profit: float = None
    pnl: float = None
    liquidation_price: float = None

    def calculate_profit(self):
        self.profit = (np.exp(np.log(self.exit_price / self.entry_price) * self.side) - 1) \
                      * self.units * self.entry_price

    def calculate_pnl_pct(self, prev_amount, leverage):

        if self.amount is None:
            return

        self.pnl = (self.amount - prev_amount) / prev_amount * leverage
