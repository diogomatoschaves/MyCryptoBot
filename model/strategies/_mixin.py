import numpy as np
import pandas as pd


class StrategyMixin:
    """
    A mixin class that provides basic functionality for backtesting trading strategies.

    Parameters
    ----------
    data : pd.DataFrame, optional
        The DataFrame containing the historical price data for the asset.
    close_col : str, optional
        The name of the column in the data that contains the price data.
    returns_col : str, optional
        The name of the column in the data that will contain the returns data.

    Attributes
    ----------
    data : pd.DataFrame
        The DataFrame containing the historical price data for the asset.
    close_col : str
        The name of the column in the data that contains the price data.
    returns_col : str
        The name of the column in the data that will contain the returns data.
    symbol : str
        The name of the asset being traded.

    Methods
    -------
    _get_test_title(self)
        Return a string with the title for the backtest.
    _get_data() -> pd.DataFrame
        Returns the current DataFrame containing the historical price data for the asset.
    set_data(data: pd.DataFrame) -> None
        Sets the DataFrame containing the historical price data for the asset.
    set_parameters(params: dict, data: pd.DataFrame) -> None
        Updates the parameters of the strategy.
    _calculate_returns() -> None
        Calculates the returns of the asset and updates the data DataFrame.
    update_data() -> None
        Updates the data DataFrame by calculating the returns of the asset.

    """

    def __init__(
        self,
        data=None,
        trade_on_close=True,
        close_col='close',
        open_col='open',
        high_col='high',
        low_col='low',
        returns_col='returns'
    ):
        """
        Initializes a new instance of the StrategyMixin class.

        Parameters
        ----------
        data : pd.DataFrame, optional
            The DataFrame containing the historical price data for the asset.
        close_col : str, optional
            The name of the column in the data that contains the close price data.
        open_col : str, optional
            The name of the column in the data that contains the open price data.
        high_col : str, optional
            The name of the column in the data that contains the high price data.
        low_col : str, optional
            The name of the column in the data that contains the low price data.
        returns_col : str, optional
            The name of the column in the data that will contain the returns' data.
        """

        self.close_col = close_col
        self.open_col = open_col
        self.high_col = high_col
        self.low_col = low_col
        self.trade_on_close = trade_on_close
        self.price_col = close_col if trade_on_close else open_col
        self.returns_col = returns_col
        self.symbol = None

        if data is not None:
            self.data = self.update_data(data.copy())

    def __repr__(self):
        """
        Returns a string representation of the strategy.

        Returns:
        --------
        str:
            A string representation of the strategy.
        """
        return "{}".format(self.__class__.__name__)

    def get_params(self, **kwargs):
        return self.params if self.params else {}

    def _get_test_title(self):
        """
        Returns the title for the backtest report.

        Returns:
        --------
        str:
            The title for the backtest report.
        """
        return f"{self.__repr__()} strategy backtest."

    def _get_data(self) -> pd.DataFrame:
        """
        Returns the current DataFrame containing the historical price data for the asset.

        Returns
        -------
        pd.DataFrame
            The current DataFrame containing the historical price data for the asset.
        """

        return self.data

    def set_data(self, data: pd.DataFrame, strategy_obj=None) -> None:
        """
        Sets the DataFrame containing the historical price data for the asset.

        Parameters
        ----------
        data : pd.DataFrame
            The DataFrame containing the historical price data for the asset.
        strategy_obj : Strategy object

        """

        if data is not None:
            if strategy_obj is not None:
                strategy_obj.data = strategy_obj.update_data(data.copy())
            else:
                self.data = self.update_data(self.data.copy())

    def set_parameters(self, params=None, data=None) -> None:
        """
        Updates the parameters of the strategy.

        Parameters
        ----------
        data
        params : dict, optional
            A dictionary containing the parameters to be updated.
        """

        if params is None:
            return

        for param, new_value in params.items():
            setattr(self, f"_{param}", self.get_params()[param](new_value))

        data = data.copy() if data is not None else self.data.copy()

        self.data = self.update_data(data)

    def _calculate_returns(self, data) -> pd.DataFrame:
        """
        Calculates the returns of the asset and updates the data DataFrame.
        """

        if self.trade_on_close:
            data[self.returns_col] = np.log(data[self.price_col] / data[self.price_col].shift(1))
        else:
            data[self.returns_col] = np.log(data[self.price_col].shift(-1) / data[self.price_col])
            data.loc[data.index[-1], self.returns_col] = \
                np.log(data.loc[data.index[-1], self.close_col] / data.loc[data.index[-1], self.open_col])

        return data

    def update_data(self, data) -> pd.DataFrame:
        """
        Updates the input data with additional columns required for the strategy.

        Parameters
        ----------
        data : pd.DataFrame
            OHLCV data to be updated.

        Returns
        -------
        pd.DataFrame
            Updated OHLCV data containing additional columns.
        """

        return self._calculate_returns(data)
