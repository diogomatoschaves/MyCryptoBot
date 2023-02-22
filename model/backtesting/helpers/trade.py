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
    """

    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    units: int
    direction: int
