from typing import Literal

import numpy as np
import pandas as pd

from model.strategies._mixin import StrategyMixin
from model.strategies.properties import STRATEGIES
from shared.utils.exceptions import StrategyInvalid, StrategyRequired

possible_methods = ["Unanimous", "Majority"]


class StrategyCombiner(StrategyMixin):
    """
    Combines multiple strategies and determines the combined side based on a specified method.

    Parameters:
    -----------
    strategies : iterable
        List of strategy objects to be combined.
    method : Literal["Unanimous", "Majority"], optional
        The method used to determine the combined side (default is 'Majority').
    data : pd.DataFrame, optional
        Historical price data for the asset (default is None).
    **kwargs : additional keyword arguments
        Additional arguments to be passed to the StrategyMixin constructor.

    Attributes:
    -----------
    strategies : iterable
        List of strategy objects being combined.
    method : Literal["Unanimous", "Majority"]
        The method used to determine the combined side.
    data : pd.DataFrame
        Current DataFrame containing historical price data for the asset.

    Methods:
    --------
    __repr__():
        Returns a formatted string representation of the StrategyCombiner object.
    get_params(**kwargs):
        Returns parameters of a specific strategy within the combiner.
    _get_test_title():
        Returns the title for the backtest report.
    _get_data() -> pd.DataFrame:
        Returns the current DataFrame containing the historical price data.
    set_data(data, strategy_obj=None):
        Sets historical price data and updates strategy positions.
    set_parameters(params=None, data=None):
        Sets parameters for individual strategies within the combiner.
    calculate_positions(data) -> pd.DataFrame:
        Calculates the combined positions based on the specified method.
    get_signal(row=None) -> int:
        Returns the combined signal for a specific row of data.

    Examples:
    ---------
    >>> from model.strategies import Momentum, MovingAverageCrossover
    >>> from model.backtesting.combining import StrategyCombiner
    >>> strategy1 = Momentum(window=5)
    >>> strategy2 = MovingAverageCrossover(sma_s=10, sma_l=20)
    >>> combiner = StrategyCombiner([strategy1, strategy2], method='Majority')
    """

    def __init__(
        self,
        strategies,
        method: Literal["Unanimous", "Majority"] = 'Majority',
        data=None,
        **kwargs
    ):
        """
        Initialize the StrategyCombiner object.

        Parameters:
        -----------
        strategies : iterable
            List of strategy objects to be combined.
        method : Literal["Unanimous", "Majority"], optional
            The method used to determine the combined side (default is 'Majority').
        data : pd.DataFrame, optional
            Historical price data for the asset (default is None).
        **kwargs : additional keyword arguments
            Additional arguments to be passed to the StrategyMixin constructor.
        """

        StrategyMixin.__init__(self, data, **kwargs)

        self._check_input(strategies, method)

        self.strategies = strategies
        self.method = method

        if data is not None:
            self.set_data(data)

    def __repr__(self):
        """
        Returns a formatted string representation of the StrategyCombiner object.
        """
        return self._get_test_title()

    @staticmethod
    def _check_input(strategies, method):
        """
        Checks the validity of input strategies and method.

        Parameters:
        -----------
        strategies : iterable
            List of strategy objects to be combined.
        method : Literal["Unanimous", "Majority"]
            The method used to determine the combined side.

        Raises:
        -------
        Exception
            If strategies are not iterable or if method is invalid.
        StrategyRequired
            If no strategies are provided.
        StrategyInvalid
            If any strategy is not a valid strategy object.
        """

        if not isinstance(strategies, (list, tuple, type(np.array([])))):
            raise Exception("'strategies' must be an iterable of strategy objects.")

        if len(strategies) == 0:
            raise StrategyRequired

        for strategy in strategies:
            if strategy.__class__.__name__ not in STRATEGIES:
                raise StrategyInvalid(strategy.__class__.__name__)

        if method not in possible_methods:
            raise Exception(f"'method' must be one of {possible_methods}")

    def get_params(self, **kwargs):
        """
        Returns parameters of a specific strategy within the combiner.

        Parameters:
        -----------
        **kwargs : additional keyword arguments
            Specific arguments to identify the strategy.

        Returns:
        --------
        dict
            Parameters of the identified strategy.

        Raises:
        -------
        KeyError
            If the specified strategy index is not present.
        """
        strategy_index = kwargs["strategy_index"]

        return self.strategies[strategy_index].get_params()

    def _get_test_title(self):
        """
        Returns the title for the backtest report.

        Returns:
        --------
        str:
            The title for the backtest report.
        """

        title = ("Multiple Strategy Backtest: <br>" +
                 "<br>".join([f"Strategy {i + 1}: {strategy.__repr__()}" for i, strategy in enumerate(self.strategies)]))

        return title

    def _get_data(self) -> pd.DataFrame:
        """
        Returns the current DataFrame containing the historical price data for the asset.

        Returns
        -------
        pd.DataFrame
            The current DataFrame containing the historical price data for the asset.
        """

        return self.data

    def set_data(self, data, strategy_obj=None):
        """
        Sets historical price data and updates strategy positions.

        Parameters:
        -----------
        data : pd.DataFrame
            Historical price data for the asset.
        strategy_obj : object, optional
            Specific strategy object to update data (default is None).

        """

        self.data = data.copy()
        self.data = self._calculate_returns(self.data)
        self.data["side"] = 0

        for i, strategy in enumerate(self.strategies):
            strategy.data = strategy.update_data(data.copy())
            strategy.data = strategy.calculate_positions(strategy.data)
            strategy.data = strategy.data.dropna()
            strategy.symbol = self.symbol

            self.data = self.data.join(strategy.data["side"], rsuffix=f"_{i + 1}", how='inner')

    def set_parameters(self, params=None, data=None):
        """
        Sets parameters for individual strategies within the combiner.

        Parameters:
        -----------
        params : list, optional
            List of dictionaries containing parameters for each strategy (default is None).
        data : pd.DataFrame, optional
            Historical price data for the asset (default is None).
        """
        if params is None:
            return

        for i, strategy_params in enumerate(params):
            strategy = self.strategies[i]
            for param, new_value in strategy_params.items():
                setattr(strategy, f"_{param}", strategy.get_params()[param](new_value))

        self.set_data(data if data is not None else self.data)

    @staticmethod
    def get_majority_position(data, position_cols):
        """
        Calculates the combined side using the 'Majority' method.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing strategy positions.
        position_cols : list
            List of column names containing individual strategy positions.

        Returns:
        --------
        int, np.ndarray
            Combined side based on the 'Majority' method.
        """
        return np.sign(sum([data[position_col] for position_col in position_cols]))

    @staticmethod
    def get_unanimous_position(data, position_cols):
        """
        Calculates the combined side using the 'Unanimous' method.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing strategy positions.
        position_cols : list
            List of column names containing individual strategy positions.

        Returns:
        --------
        int, np.ndarray
            Combined side based on the 'Unanimous' method.
        """
        side = data[position_cols[0]]
        condition = True
        for position_col in position_cols[1:]:
            condition = np.logical_and(condition, side == data[position_col])

        return np.where(condition, side, 0)

    def calculate_positions(self, data):
        """
        Calculates the combined positions based on the specified method.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing strategy positions.

        Returns:
        --------
        pd.DataFrame
            DataFrame with the calculated combined positions.
        """

        position_cols = [col for col in data.columns if "side" in col][1:]  # Excludes 'side' column

        if self.method == 'Majority':

            data["side"] = self.get_majority_position(data, position_cols)

        elif self.method == 'Unanimous':

            data["side"] = self.get_unanimous_position(data, position_cols)

        return data

    def get_signal(self, row=None):
        """
        Returns the combined signal for a specific row of data.

        Parameters:
        -----------
        row : pd.Series, optional
            Specific row of data to calculate the combined signal (default is None, uses the last row).

        Returns:
        --------
        int
            Combined signal for the specified row.

        """

        if row is None:
            row = self.data.iloc[-1]

        positions_cols = [col for col in row.index if "side" in col][1:]

        signal = 0
        if self.method == 'Unanimous':
            signal = self.get_unanimous_position(row, positions_cols)
        elif self.method == 'Majority':
            signal = self.get_majority_position(row, positions_cols)

        return int(signal)
