import numpy as np
import pandas as pd


class StrategyMixin:
    """
    A mixin class that provides basic functionality for backtesting trading strategies.

    Parameters
    ----------
    data : pd.DataFrame, optional
        The DataFrame containing the historical price data for the asset.
    price_col : str, optional
        The name of the column in the data that contains the price data.
    returns_col : str, optional
        The name of the column in the data that will contain the returns data.

    Attributes
    ----------
    data : pd.DataFrame
        The DataFrame containing the historical price data for the asset.
    price_col : str
        The name of the column in the data that contains the price data.
    returns_col : str
        The name of the column in the data that will contain the returns data.
    symbol : str
        The name of the asset being traded.

    Methods
    -------
    _get_data() -> pd.DataFrame
        Returns the current DataFrame containing the historical price data for the asset.
    set_data(data: pd.DataFrame) -> None
        Sets the DataFrame containing the historical price data for the asset.
    set_parameters(params: dict) -> None
        Updates the parameters of the strategy.
    _calculate_returns() -> None
        Calculates the returns of the asset and updates the data DataFrame.
    update_data() -> None
        Updates the data DataFrame by calculating the returns of the asset.

    """

    def __init__(self, data=None, price_col='close', returns_col='returns'):
        """
        Initializes a new instance of the StrategyMixin class.

        Parameters
        ----------
        data : pd.DataFrame, optional
            The DataFrame containing the historical price data for the asset.
        price_col : str, optional
            The name of the column in the data that contains the price data.
        returns_col : str, optional
            The name of the column in the data that will contain the returns data.
        """

        self.price_col = price_col
        self.returns_col = returns_col
        self.symbol = None

        if data is not None:
            self.data = data.copy()
            self.update_data()

    def _get_data(self) -> pd.DataFrame:
        """
        Returns the current DataFrame containing the historical price data for the asset.

        Returns
        -------
        pd.DataFrame
            The current DataFrame containing the historical price data for the asset.
        """

        return self.data

    def set_data(self, data: pd.DataFrame) -> None:
        """
        Sets the DataFrame containing the historical price data for the asset.

        Parameters
        ----------
        data : pd.DataFrame
            The DataFrame containing the historical price data for the asset.
        """

        if data is not None:
            self.data = data
            self.data = self.update_data()

    def set_parameters(self, params=None) -> None:
        """
        Updates the parameters of the strategy.

        Parameters
        ----------
        params : dict, optional
            A dictionary containing the parameters to be updated.
        """

        if params is None:
            return

        for param, new_value in params.items():
            setattr(self, f"_{param}", self.params[param](new_value))

        self.update_data()

    def _calculate_returns(self) -> None:
        """
        Calculates the returns of the asset and updates the data DataFrame.
        """

        data = self.data

        data[self.returns_col] = np.log(data[self.price_col] / data[self.price_col].shift(1))

        self.data = data

    def update_data(self) -> None:
        """
        Updates the data DataFrame by calculating the returns of the asset.
        """

        self._calculate_returns()
