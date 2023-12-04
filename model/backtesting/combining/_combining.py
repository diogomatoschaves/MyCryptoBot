from typing import Literal

import numpy as np
import pandas as pd

from model.strategies._mixin import StrategyMixin
from model.strategies.properties import STRATEGIES
from shared.utils.exceptions import StrategyInvalid, StrategyRequired


possible_methods = ["Unanimous", "Majority"]


class StrategyCombiner(StrategyMixin):

    def __init__(
        self,
        strategies,
        method: Literal["Unanimous", "Majority"] = 'Majority',
        data=None,
        **kwargs
    ):

        StrategyMixin.__init__(self, data, **kwargs)

        self._check_input(strategies, method)

        self.strategies = strategies
        self.method = method

    def __repr__(self):
        return self._get_test_title()

    @staticmethod
    def _check_input(strategies, method):

        if not isinstance(strategies, (list, tuple, type(np.array([])))):
            raise Exception("'strategies' must be an iterable of strategy objects.")

        if len(strategies) == 0:
            raise StrategyRequired

        for strategy in strategies:
            if strategy.__class__.__name__ not in STRATEGIES:
                raise StrategyInvalid(strategy.__class__.__name__)

        if method not in possible_methods:
            raise Exception(f"'method' must be one of {possible_methods}")

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

        self.data = data.copy()
        self.data = self._calculate_returns(self.data)
        self.data["position"] = 0

        for i, strategy in enumerate(self.strategies):
            strategy.data = strategy.update_data(data.copy())
            strategy.data = strategy._calculate_positions(strategy.data)
            strategy.data = strategy.data.dropna()

            self.data = self.data.join(strategy.data["position"], rsuffix=f"_{i + 1}", how='inner')

    def set_parameters(self, params=None):
        return

    def _calculate_positions(self, data):

        position_cols = [col for col in data.columns if "position" in col][1:]  # Excludes 'position' column

        if self.method == 'Majority':

            data["position"] = np.sign(sum([data[position_col] for position_col in position_cols]))

        elif self.method == 'Unanimous':

            position = data[position_cols[0]]
            condition = True
            for position_col in position_cols[1:]:
                condition = np.logical_and(condition, position == data[position_col])

            data["position"] = np.where(condition, position, 0)

        return data
