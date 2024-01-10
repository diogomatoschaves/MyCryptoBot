import numpy as np
import pandas as pd

exception_message = 'The provided exchange is not supported.'


def get_maintenance_margin(symbol_brackets, notional_value, exchange='binance'):
    """
    Calculate the maintenance margin rate and amount based on symbol brackets and notional value.

    Parameters
    ----------
    symbol_brackets: pd.DataFrame
        DataFrame containing symbol brackets with columns ['notionalFloor', 'maintMarginRatio', 'cum'].
    notional_value: pd.Series
        Series containing notional values for calculation.
    exchange: str, optional
        Exchange name. Default is 'binance'.

    Returns:
    --------
    Tuple of maintenance rate and maintenance amount.
    """
    def get_maintenance_margin_binance():
        """
        Internal function for calculating maintenance margin for Binance exchange.
        """

        # values = pd.concat([pd.DataFrame(notional_value).T] * len(notional_value)).T
        #
        # triangular_matrix = pd.DataFrame(np.tril(values))

        values = pd.Series(notional_value)

        comparison = pd.DataFrame()
        for i, notional_floor in enumerate(symbol_brackets['notionalFloor']):
            comparison[i] = values >= notional_floor

        # greater_than = triangular_matrix.gt(symbol_brackets["notionalFloor"], axis=1)

        indexes = comparison.idxmin(axis=1) - 1

        brackets = symbol_brackets.iloc[indexes, :]

        maintenance_rate = brackets["maintMarginRatio"].values
        maintenance_amount = brackets["cum"].values

        return maintenance_rate, maintenance_amount

    if exchange == 'binance':
        return get_maintenance_margin_binance()
    else:
        raise Exception(exception_message)


def calculate_margin_ratio(
    leverage,
    units,
    side,
    entry_price,
    mark_price,
    maintenance_rate,
    maintenance_amount,
    exchange
):
    """
    Calculate the margin ratio based on provided parameters.

    Parameters
    ----------
    leverage: float
        Leverage used for the position.
    units: float
        Number of units in the position.
    side: int
        Trading side (-1 for short, 1 for long).
    entry_price: float
        Entry price of the position.
    mark_price: float
        Mark price of the position.
    maintenance_rate: float
        Maintenance margin rate.
    maintenance_amount: float
        Maintenance margin amount.
    exchange: str
        Exchange name.

    Returns:
    --------
    Float representing the margin ratio.
    """
    def calculate_margin_ratio_binance():
        """
        Internal function for calculating margin ratio for Binance exchange.
        """
        initial_value = units * entry_price
        current_value = units * mark_price
        initial_margin = initial_value / leverage

        margin_balance = initial_margin + (current_value - initial_value) * side

        maintenance_margin = current_value * maintenance_rate - maintenance_amount

        try:
            return maintenance_margin / margin_balance
        except ZeroDivisionError:
            return np.Inf

    if exchange == 'binance':
        return calculate_margin_ratio_binance()
    else:
        raise Exception(exception_message)


def calculate_liquidation_price(
    units,
    entry_price,
    side,
    leverage,
    maintenance_rate,
    maintenance_amount,
    exchange
):
    """
    Calculate the liquidation price based on provided parameters.

    Parameters
    ----------
    units: float
        Number of units in the position.
    entry_price: float
        Entry price of the position.
    side: int
        Trading side (-1 for short, 1 for long).
    leverage: float
        Leverage used for the position.
    maintenance_rate: float
        Maintenance margin rate.
    maintenance_amount: float
        Maintenance margin amount.
    exchange: str
        Exchange name.

    Returns:
    --------
    Float representing the liquidation price.
    """
    def calculate_liquidation_ratio_binance():
        """
        Internal function for calculating liquidation price ratio for Binance exchange.
        """
        notional_value = units * entry_price
        wallet_balance = notional_value / leverage

        try:
            liquidation_price = ((wallet_balance + maintenance_amount - side * units * entry_price) /
                                 (units * maintenance_rate - side * units))
        except ZeroDivisionError:
            liquidation_price = 0

        return liquidation_price

    if exchange == 'binance':
        return calculate_liquidation_ratio_binance()
    else:
        raise Exception(exception_message)
