import numpy as np
from model.backtesting._mixin import BacktestMixin
from model.backtesting.helpers import Trade


class VectorizedBacktester(BacktestMixin):
    """ Class for vectorized backtesting.
    """

    def __init__(self, strategy, symbol=None, amount=1000, trading_costs=0.0):
        """

        Parameters
        ----------
        strategy : StrategyType
            A valid strategy class as defined in model.strategies __init__ file.
        symbol : string
            Symbol for which we are performing the backtest. default is None.
        trading_costs : int
            The trading cost per trade in percentage of the value being traded.
        """

        BacktestMixin.__init__(self, symbol, amount, trading_costs)

        self.strategy = strategy
        self.strategy.symbol = symbol

    def __repr__(self):
        return self.strategy.__repr__()

    def _test_strategy(self, params=None, print_results=True, plot_results=True, plot_positions=False):
        """

        Parameters
        ----------
        params : dict
            Dictionary containing the keywords and respective values of the parameters to be updated.
        plot_results: boolean
            Flag for whether to plot the results of the backtest.
        plot_positions : boolean
            Flag for whether to plot the positions markers on the results plot.

        """

        self.set_parameters(params)

        data = self._get_data().dropna().copy()

        if data.empty:
            return 0, 0

        processed_data = self._vectorized_backtest(data)

        results, nr_trades, perf, outperf = self._evaluate_backtest(processed_data)

        self._print_results(results, print_results)

        self.plot_results(self.processed_data, plot_results, plot_positions)

        return perf, outperf, results

    def _vectorized_backtest(self, data):
        """
        Assess the performance of the trading strategy on historical data.

        Parameters:
        -----------
        data : pandas.DataFrame
            Historical price data for the trading symbol. Pre sanitized.

        Returns:
        --------
        None
        """
        data = self._calculate_positions(data)
        data["trades"] = data.position.diff().fillna(0).abs()
        data.loc[data.index[0], "trades"] = np.abs(data.iloc[0]["position"])
        data.loc[data.index[-1], "trades"] = np.abs(data.iloc[-2]["position"])
        data.loc[data.index[-1], "position"] = 0

        data["trades"] = data["trades"].astype('int')
        data["position"] = data["position"].astype('int')

        data["strategy_returns"] = (data.position.shift(1) * data.returns).fillna(0)
        data["strategy_returns_tc"] = (data["strategy_returns"] - data["trades"] * self.tc).fillna(0)

        data.loc[data.index[0], "returns"] = 0

        data["accumulated_returns"] = data[self.returns_col].cumsum().apply(np.exp).fillna(1)
        data["accumulated_strategy_returns"] = data["strategy_returns"].cumsum().apply(np.exp).fillna(1)
        data["accumulated_strategy_returns_tc"] = data["strategy_returns_tc"].cumsum().apply(np.exp).fillna(1)

        return data

    def _retrieve_trades(self, processed_data, trading_costs=0):
        """
        Computes the trades made based on the input processed data and returns a list of Trade objects.

        Parameters
        ----------
        processed_data : pandas.DataFrame
            The DataFrame containing the processed data for the strategy backtest.
        trading_costs: float
            The trading costs as a raw percent value of each trade.

        Returns
        -------
        trades_list : list of Trade objects
            A list containing information about each trade made during the backtest, represented as Trade objects.
            Each Trade object has the following attributes:

            - entry_price (float): The price at which the trade was entered.
            - entry_date (datetime): The date at which the trade was entered.
            - exit_price (float): The price at which the trade was exited.
            - exit_date (datetime): The date at which the trade was exited.
            - direction (int): The direction of the trade (1 for long, -1 for short).
            - units (float): The number of units of the asset traded.

        """

        cols = [self.price_col, "position", "accumulated_strategy_returns"]

        processed_data = processed_data.copy()

        if not self.trade_on_close:
            processed_data[self.price_col] = processed_data[self.price_col].shift(-1)

        trades = processed_data[processed_data.trades != 0][cols]

        trades = trades.reset_index()

        col = list(set(trades.columns).difference(set(cols)))[0]

        trades = trades.rename(columns={self.price_col: "entry_price", col: "entry_date", "position": "direction"})
        trades["exit_price"] = trades["entry_price"].shift(-1) * (1 - trading_costs * trades["direction"])
        trades["entry_price"] = trades["entry_price"] * (1 + trading_costs * trades["direction"])
        trades["exit_date"] = trades["entry_date"].shift(-1)
        trades = trades[trades.direction != 0]

        trades["exit_price"] = np.where(
            np.isnan(trades['exit_price']),
            processed_data.loc[processed_data.index[-1], self.close_col],
            trades['exit_price']
        )

        trades = trades.reset_index(drop=True)
        trades = trades.dropna()

        trades["simple_return"] = (trades["exit_price"] - trades["entry_price"]) / trades["entry_price"]
        trades["log_return"] = np.log(trades["exit_price"] / trades["entry_price"]) * trades["direction"]

        trades["simple_cum"] = (trades["simple_return"] * trades["direction"] + 1).cumprod()
        trades["log_cum"] = trades["log_return"].cumsum().apply(np.exp)

        if len(trades) > 0:
            trades["amount"] = self.amount * trades["log_cum"]
            trades["units"] = (trades["amount"].shift(1) / trades["entry_price"]).fillna(self.amount / trades["entry_price"][0])
            trades["profit"] = (trades["amount"] - trades["amount"].shift(1)).fillna(trades["amount"][0] - self.amount)

        self._trades_df = trades.copy()

        trades.drop(
            ['simple_return', 'simple_cum', 'log_return', 'log_cum', 'accumulated_strategy_returns'],
            axis=1, inplace=True
        )

        trades_list = [Trade(**row) for _, row in trades.iterrows()]

        return trades_list

    def _evaluate_backtest(self, processed_data):
        """
       Evaluates the performance of the trading strategy on the backtest run.

       Parameters:
       -----------
       print_results : bool, default True
           Whether to print the results.

       Returns:
       --------
       float
           The performance of the strategy.
       float
           The out-/underperformance of the strategy.
       """

        self.processed_data = processed_data

        nr_trades = self._get_nr_trades(processed_data)

        self.trades = self._retrieve_trades(processed_data, self.tc)

        # absolute performance of the strategy
        perf = processed_data["accumulated_strategy_returns_tc"].iloc[-1]

        # out-/underperformance of strategy
        outperf = perf - processed_data["accumulated_returns"].iloc[-1]

        results = self._get_results(self.trades, processed_data)

        return results, nr_trades, perf, outperf
    
    @staticmethod
    def _get_nr_trades(data):
        return int(data["trades"].sum() / 2) + 1
