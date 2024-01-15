import numpy as np
from model.backtesting._mixin import BacktestMixin
from model.backtesting.helpers import Trade
from model.backtesting.helpers.margin import get_maintenance_margin, calculate_liquidation_price, calculate_margin_ratio


class VectorizedBacktester(BacktestMixin):
    """ Class for vectorized backtesting.
    """

    def __init__(
        self,
        strategy,
        symbol=None,
        amount=1000,
        trading_costs=0.0,
        include_margin=False,
        leverage=1
    ):
        """

        Parameters
        ----------
        strategy : StrategyType
            A valid strategy class as defined in model.strategies __init__ file.
        symbol : string
            Symbol for which we are performing the backtest. default is None.
        amount : float, optional
            The initial amount of currency to be traded with. Default is 1000.
        trading_costs : float
            The trading cost per trade in percentage of the value being traded.
        """

        BacktestMixin.__init__(self, symbol, amount, trading_costs, include_margin, leverage)

        self.strategy = strategy

        if symbol is not None:
            self.strategy.symbol = symbol

    def _test_strategy(self, params=None, print_results=True, plot_results=True, show_plot_no_tc=False):
        """
        Parameters
        ----------
        params : dict
            Dictionary containing the keywords and respective values of the parameters to be updated.
        print_results: bool, optional
            Flag for whether to print the results of the backtest.
        plot_results: boolean
            Flag for whether to plot the results of the backtest.
        show_plot_no_tc: bool, optional
            Whether to plot the equity curve without the trading_costs applied

        """
        self._fix_original_data()

        self.set_parameters(params, data=self._original_data.copy())

        data = self._get_data().dropna().copy()

        if data.empty:
            return 0, 0

        processed_data = self._vectorized_backtest(data)

        results, nr_trades, perf, outperf = self._evaluate_backtest(processed_data)

        self._print_results(results, print_results)

        self.plot_results(self.processed_data, plot_results, show_plot_no_tc=show_plot_no_tc)

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
        data = self.calculate_positions(data)
        data["trades"] = data.side.diff().fillna(0).abs()
        data.loc[data.index[0], "trades"] = np.abs(data.iloc[0]["side"])
        data.loc[data.index[-1], "trades"] = np.abs(data.iloc[-2]["side"])
        data.loc[data.index[-1], "side"] = 0

        data["trades"] = data["trades"].astype('int')
        data["side"] = data["side"].astype('int')

        data["strategy_returns"] = (data.side.shift(1) * data.returns).fillna(0)
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
            - side (int): The side of the trade (1 for long, -1 for short).
            - units (float): The number of units of the asset traded.

        """

        cols = [self.price_col, "side", "accumulated_strategy_returns"]

        processed_data = processed_data.copy()

        if not self.trade_on_close:
            processed_data[self.price_col] = processed_data[self.price_col].shift(-1)

        trades = processed_data[processed_data.trades != 0][cols]

        trades = trades.reset_index()

        col = list(set(trades.columns).difference(set(cols)))[0]

        trades = trades.rename(columns={self.price_col: "entry_price", col: "entry_date"})
        trades["exit_price"] = trades["entry_price"].shift(-1) * (1 - trading_costs * trades["side"])
        trades["entry_price"] = trades["entry_price"] * (1 + trading_costs * trades["side"])
        trades["exit_date"] = trades["entry_date"].shift(-1)
        trades = trades[trades.side != 0]

        trades["exit_price"] = np.where(
            np.isnan(trades['exit_price']),
            processed_data.loc[processed_data.index[-1], self.close_col],
            trades['exit_price']
        )

        trades = trades.reset_index(drop=True)
        trades = trades.dropna()

        trades["simple_return"] = (trades["exit_price"] - trades["entry_price"]) / trades["entry_price"]
        trades["log_return"] = np.log(trades["exit_price"] / trades["entry_price"]) * trades["side"]

        trades["simple_cum"] = (trades["simple_return"] * trades["side"] + 1).cumprod()
        trades["log_cum"] = trades["log_return"].cumsum().apply(np.exp)

        if len(trades) > 0:
            trades["amount"] = self.amount * trades["log_cum"]
            trades["units"] = (trades["amount"].shift(1) / trades["entry_price"]).fillna(self.amount / trades["entry_price"][0])
            trades["profit"] = (trades["amount"] - trades["amount"].shift(1)).fillna(trades["amount"][0] - self.amount)
            trades["pnl"] = ((trades["amount"] - trades["amount"].shift(1)) / trades["amount"].shift(1))\
                .fillna((trades["amount"][0] - self.amount) / self.amount) * self.leverage

        columns_to_delete = [
                'simple_return',
                'simple_cum',
                'log_return',
                'log_cum',
                'accumulated_strategy_returns',
            ]

        if self.include_margin and len(trades) > 0:
            trades['maintenance_rate'], trades['maintenance_amount'] = get_maintenance_margin(
                self._symbol_bracket,
                trades['units'] * trades['entry_price'],
                self.exchange
            )

            trades['liquidation_price'] = calculate_liquidation_price(
                trades['units'],
                trades['entry_price'],
                trades['side'],
                self.leverage,
                trades['maintenance_rate'],
                trades['maintenance_amount'],
                exchange=self.exchange
            )

            columns_to_delete.extend(['maintenance_rate', 'maintenance_amount'])

        self._trades_df = trades.copy()

        trades.drop(columns_to_delete, axis=1, inplace=True)

        trades_list = [Trade(**row) for _, row in trades.iterrows()]

        return trades_list

    def _calculate_margin_ratio(self, trades_df, processed_data):

        df = processed_data.copy()

        if len(trades_df) == 0:
            df["margin_ratios"] = 0
            return df

        df['entry_price'] = None
        df['units'] = None
        df['maintenance_rate'] = None
        df['maintenance_amount'] = None
        df['mark_price'] = np.where(df['side'] == 1, df[self.low_col], df[self.high_col])

        df_filter = (df.trades != 0) & (df.side != 0)

        df.loc[df[df_filter].index, 'entry_price'] = trades_df['entry_price'].values
        df.loc[df[df_filter].index, 'units'] = trades_df['units'].values
        df.loc[df[df_filter].index, 'maintenance_rate'] = trades_df['maintenance_rate'].values
        df.loc[df[df_filter].index, 'maintenance_amount'] = trades_df['maintenance_amount'].values

        df['entry_price'].ffill(inplace=True)
        df['units'].ffill(inplace=True)
        df['maintenance_rate'].ffill(inplace=True)
        df['maintenance_amount'].ffill(inplace=True)

        df['margin_ratios'] = calculate_margin_ratio(
            self.leverage,
            df['units'],
            df['side'],
            df['entry_price'],
            df['mark_price'],
            df['maintenance_rate'],
            df['maintenance_amount'],
            exchange=self.exchange
        )

        df.drop(
            ['entry_price', 'units', 'mark_price', 'maintenance_rate', 'maintenance_amount'],
            axis=1, inplace=True
        )

        df["margin_ratios"] = np.where(df["margin_ratios"] > 1, 1, df["margin_ratios"])
        df["margin_ratios"] = np.where(df["margin_ratios"] < 0, 1, df["margin_ratios"])
        df["margin_ratios"] = np.where(df["side"] == 0, 0, df["margin_ratios"])

        df["margin_ratios"] = df["margin_ratios"].fillna(0)

        return df

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

        if self.include_margin:
            self.processed_data = self._calculate_margin_ratio(self._trades_df, self.processed_data)

        # absolute performance of the strategy
        perf = processed_data["accumulated_strategy_returns_tc"].iloc[-1]

        # out-/underperformance of strategy
        outperf = perf - processed_data["accumulated_returns"].iloc[-1]

        results = self._get_results(self.trades, processed_data)

        return results, nr_trades, perf, outperf
    
    @staticmethod
    def _get_nr_trades(data):
        return int(data["trades"].sum() / 2) + 1
