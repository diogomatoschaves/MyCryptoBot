import numpy as np

from model.backtesting._mixin import BacktestMixin
from model.backtesting.helpers import Trade
from model.backtesting.helpers.margin import calculate_margin_ratio, get_maintenance_margin, calculate_liquidation_price
from shared.trading import Trader


class IterativeBacktester(BacktestMixin, Trader):
    """
    A class for backtesting trading strategies iteratively using historical data.
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
        Initializes the IterativeBacktester object.

        Parameters
        ----------
        strategy : object
            The trading strategy to be tested.
        symbol : str, optional
            The trading symbol. Default is None.
        amount : float, optional
            The initial amount of currency to be traded with. Default is 1000.
        trading_costs : float, optional
            The percentage of trading costs. Default is 0.
        """

        BacktestMixin.__init__(self, symbol, amount, trading_costs, include_margin, leverage)
        Trader.__init__(self, amount)

        self.strategy = strategy

        if symbol is not None:
            self.strategy.symbol = symbol

        self.positions_lst = []
        self._equity = [self.amount]
        self.margin_ratios = []
        self.returns = []
        self.strategy_returns = []
        self.strategy_returns_tc = []
        self.positions = {
            symbol: 0
        }

    def _set_position(self, symbol, value, **kwargs):
        """
        Sets the side for the given symbol.

        Parameters
        ----------
        symbol : str
            The trading symbol.
        value : int
            The side value.
        """
        self.positions[symbol] = value

    def _get_position(self, symbol):
        """
        Gets the side for the given symbol.

        Parameters
        ----------
        symbol : str
            The trading symbol.

        Returns
        -------
        float
            The side value.
        """
        return self.positions[symbol]

    def _reset_object(self):
        """
        Resets the object attributes to their initial values.
        """
        self._set_position(self.symbol, 0)  # initial neutral side
        self._equity = [self.amount]
        self.margin_ratios = []
        self.strategy_returns = []
        self.strategy_returns_tc = []
        self.positions_lst = [0]
        self.nr_trades = 0
        self.trades = []
        self.current_balance = self.initial_balance
        self.units = 0

    def calculate_positions(self, data):
        """
        Calculates the positions for the given data.

        Parameters
        ----------
        data : pandas.DataFrame
            The historical data.

        Returns
        -------
        pandas.DataFrame
            The data with the calculated positions.
        """
        data["side"] = self.positions_lst
        return data

    def _get_trades(self, _):
        """
        Gets the number of trades executed.

        Returns
        -------
        int
            The number of trades executed.
        """
        return self.nr_trades

    def _get_price(self, _, row):
        """
        Gets the price for the given row.

        Parameters
        ----------
        _ : str
            Not used.
        row : pandas.Series
            The data row.

        Returns
        -------
        float
            The price.
        """
        price = row[self.close_col]

        return price

    def _get_high_low_price(self, side, row):
        """
        Gets the price for the given row.

        Parameters
        ----------
        side : int
            side of trade.
        row : pandas.Series
            The data row.

        Returns
        -------
        float
            The price.
        """
        price = row[self.high_col] if side == -1 else row[self.low_col]

        return price

    def _test_strategy(self, params=None, print_results=True, plot_results=True, show_plot_no_tc=False):
        """
        Run a backtest for the given parameters and assess the performance of the strategy.

        Parameters
        ----------
        params : dict, optional
            Dictionary containing the keywords and respective values of the parameters to be updated.
        print_results: bool, optional
            Flag for whether to print the results of the backtest.
        plot_results : bool, optional
            Flag for whether to plot the results of the backtest.
        show_plot_no_tc: bool, optional
            Whether to plot the equity curve without the trading_costs applied

        Returns
        -------
        dict
            Dictionary containing the performance metrics of the backtest.

        """
        self._fix_original_data()

        self.set_parameters(params, data=self.original_data.copy())
        self._reset_object()

        # title printout
        if print_results:
            print("-" * 70)
            print(self._get_test_title())
            print("-" * 70)

        data = self._get_data().dropna().copy()

        if data.empty:
            return 0, 0, None

        processed_data = self._iterative_backtest(data, print_results)

        results, nr_trades, perf, outperf = self._evaluate_backtest(processed_data)

        self._print_results(results, print_results)

        self.plot_results(self.processed_data, plot_results, show_plot_no_tc=show_plot_no_tc)

        return perf, outperf, results

    def _iterative_backtest(self, data, print_results=True):
        """
        Iterate through the data, trade accordingly, and calculate the strategy's performance.

        Parameters
        ----------
        data : pandas.DataFrame
            Historical data used to backtest the strategy.
        print_results: bool, optional
            Flag for whether to print the results of the backtest.

        """
        for bar, (timestamp, row) in enumerate(data.iterrows()):
            signal = self.get_signal(row)

            previous_position = self._get_position(self.symbol)

            if bar != data.shape[0] - 1:
                self.trade(self.symbol, signal, timestamp, row, amount="all", print_results=print_results)
            else:
                self.close_pos(self.symbol, timestamp, row, print_results=print_results)
                self._set_position(self.symbol, 0)

            if self.include_margin:
                self._calculate_margin_ratio(row)

            new_position = self._get_position(self.symbol)

            self.positions_lst.append(new_position)

            trades = np.abs(new_position - previous_position)

            self.strategy_returns.append(row[self.returns_col] * previous_position)
            self.strategy_returns_tc.append(self.strategy_returns[-1] - trades * self.tc)

            self._equity.append(self._get_net_value(row))

        return data

    def _calculate_margin_ratio(self, row):

        try:
            current_trade = self.trades[-1]
        except IndexError:
            self.margin_ratios.append(0)
            return

        mark_price = self._get_high_low_price(current_trade.side, row)

        if current_trade.side == -1:
            a = 1

        margin_ratio = calculate_margin_ratio(
            self.leverage,
            current_trade.units,
            current_trade.side,
            current_trade.entry_price,
            mark_price,
            self.maintenance_rate,
            self.maintenance_amount,
            exchange=self.exchange
        )

        self.margin_ratios.append(margin_ratio)

    def _evaluate_backtest(self, processed_data):
        processed_data["side"] = self.positions_lst[1:]
        processed_data.loc[processed_data.index[0], "side"] = self.positions_lst[1]
        processed_data.loc[processed_data.index[0], self.returns_col] = 0

        processed_data["strategy_returns"] = self.strategy_returns
        processed_data["strategy_returns_tc"] = self.strategy_returns_tc

        processed_data["accumulated_returns"] = processed_data[self.returns_col].cumsum().apply(np.exp)
        processed_data["accumulated_strategy_returns"] = processed_data["strategy_returns"].cumsum().apply(np.exp)
        processed_data["accumulated_strategy_returns_tc"] = processed_data["strategy_returns_tc"].cumsum().apply(np.exp)

        if self.include_margin:
            processed_data["margin_ratios"] = self.margin_ratios

            processed_data["margin_ratios"] = np.where(processed_data["margin_ratios"] > 1, 1, processed_data["margin_ratios"])
            processed_data["margin_ratios"] = np.where(processed_data["margin_ratios"] < 0, 1, processed_data["margin_ratios"])
            processed_data["margin_ratios"] = np.where(processed_data["side"] == 0, 0, processed_data["margin_ratios"])

        processed_data.dropna(inplace=True)

        self.processed_data = processed_data

        returns = [np.log(trade.exit_price / trade.entry_price) * trade.side for trade in self.trades]
        perf = np.exp(np.sum(returns))  # Performance with trading_costs

        perf_bh = processed_data["accumulated_returns"].iloc[-1]

        outperf = perf - perf_bh

        results = self._get_results(self.trades, processed_data)

        return results, self.nr_trades, perf, outperf

    def _get_net_value(self, row):
        """
        Calculate the current net value of the strategy.

        Parameters
        ----------
        row : pandas.Series
            The current row of the data being processed.

        Returns
        -------
        float
            The current net value of the strategy.

        """
        price = self._get_price("", row)

        return self.current_balance + self.units * price

    def buy_instrument(
        self,
        symbol,
        date=None,
        row=None,
        units=None,
        amount=None,
        open_trade=False,
        header='',
        **kwargs
    ):
        """
        Buys a specified amount of the instrument at the given date or row. If `units` is not specified, it calculates the
        number of units to buy based on the provided `amount` and the price of the instrument. It then calculates the trading cost
        based on the amount or number of units sold, and updates the `current_balance`, `units` and `trades` attributes
        accordingly. If `print_results` is set to True in `**kwargs`, it prints a message showing the date, number of units bought
        and the buying price.

        Parameters
        ----------
        symbol : str
            The symbol of the asset being traded.
        date : str, optional
            The date of the trade.
        row : pandas.Series, optional
            The row of the data being processed.
        units : float, optional
            The number of units to buy.
        amount : float, optional
            The amount of money to spend on the purchase.
        open_trade : boolean, optional
            A trade should be opened if True, and closed if False.
        header : str, optional
            The header of the message printed to the console.
        **kwargs : dict, optional
            Additional keyword arguments.

        """
        print_results = kwargs.get('print_results')

        price = self._get_price(date, row)
        price_tc = price * (1 + self.tc)

        if units is None:
            units = amount / price_tc

        if amount is None:
            # The formula below comes from the computation: new_amount = prev_price / price * prev_amount,
            # amount = 2 * prev_amount - new_amount, prev_amount = units * prev_price
            amount = self.trades[-1].entry_price * units * (2 - self.trades[-1].entry_price / price_tc)

        self.current_balance -= amount
        self.units += units

        self._handle_trade(self.trades, open_trade, date, price_tc, units, self.current_balance, 1)

        if print_results:
            print(f"{date} |  Buying {round(units, 4)} {self.symbol} for {round(price_tc, 5)}")

    def sell_instrument(
        self,
        symbol,
        date=None,
        row=None,
        units=None,
        amount=None,
        open_trade=False,
        header='',
        **kwargs
    ):
        """
        Sells a specified amount of the instrument at the given date or row. If `units` is not specified, it calculates the
        number of units to sell based on the provided `amount` and the price of the instrument. It then calculates the trading cost
        based on the amount or number of units sold, and updates the `current_balance`, `units` and `trades` attributes
        accordingly. If `print_results` is set to True in `**kwargs`, it prints a message showing the date, number of units sold
        and the selling price.

        Parameters
        ----------
        symbol : str
            The symbol of the instrument to sell.
        date : str or None, optional
            The date to sell the instrument at, formatted as 'YYYY-MM-DD'. If None, row must be specified instead.
        row : pandas.Series, optional
            The row of the data being processed.
        units : float or None, optional
            The number of units to sell. If None, amount must be specified instead.
        amount : float or None, optional
            The total amount to use to buy units of the instrument. If None, units must be specified instead.
        open_trade : boolean, optional
            A trade should be opened if True, and closed if False.
        header : str, optional
            A header to print before the results.
        **kwargs : dict, optional
            Additional keyword arguments:
            - print_results : bool, optional
                Whether to print the results.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If both date and row are None or both units and amount are None.
        """
        print_results = kwargs.get('print_results')

        price = self._get_price(date, row)
        price_tc = price * (1 - self.tc)

        if units is None:
            units = amount / price_tc

        if amount is None:
            amount = units * price_tc

        self.current_balance += amount
        self.units -= units

        self._handle_trade(self.trades, open_trade, date, price_tc, units, amount, -1)

        if print_results:
            print(f"{date} |  Selling {round(units, 4)} {self.symbol} for {round(price_tc, 5)}")

    def close_pos(self, symbol, date=None, row=None, header='', **kwargs):
        """
        Closes the side of the specified instrument at the given date or row. If the number of units is less than or equal to
        zero, it buys the instrument to close the side, otherwise it sells it. It then calculates the performance of the
        trading account, updates the `current_balance`, `trades` and `units` attributes accordingly, and prints a message
        showing the current balance, net performance and number of trades executed.

        Parameters
        ----------
        symbol : str
            The symbol of the instrument to close the side for.
        date : str or None, optional
            The date to close the side at, formatted as 'YYYY-MM-DD'. If None, row must be specified instead.
        row : int or None, optional
            The row index to close the side at. If None, date must be specified instead.
        header : str, optional
            A header to print before the results.
        **kwargs : dict, optional
            Additional keyword arguments:
            - print_results : bool, optional
                Whether to print the results.

        Returns
        -------
        None
        """
        print_results = kwargs.get('print_results')

        if self.units != 0 and print_results:
            print(70 * "-")
            print("{} |  +++ CLOSING FINAL POSITION +++".format(date))

        if self.units < 0:
            self.buy_instrument(symbol, date, row, open_trade=False, units=-self.units)
        elif self.units > 0:
            self.sell_instrument(symbol, date, row, open_trade=False, units=self.units)

        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        if print_results:

            self.print_current_balance(date)

            print("{} |  net performance (%) = {}".format(date, round(perf, 2)))
            print("{} |  number of trades executed = {}".format(date, self.nr_trades))
            print(70 * "-")

    def _handle_trade(self, trades, open_trade, date, price, units, amount, side):
        if open_trade:
            liquidation_price = None

            if self.include_margin:

                notional_value = units * price

                maintenance_rate, maintenance_amount = get_maintenance_margin(
                    self.symbol_bracket, [notional_value], exchange=self.exchange
                )

                self.maintenance_rate = maintenance_rate[0]
                self.maintenance_amount = maintenance_amount[0]

                liquidation_price = calculate_liquidation_price(
                    units,
                    price,
                    side,
                    self.leverage,
                    maintenance_rate,
                    maintenance_amount,
                    exchange=self.exchange
                )[0]

            trades.append(Trade(date, None, price, None, units, side, None, None, None, liquidation_price))
        else:
            trades[-1].exit_date = date
            trades[-1].exit_price = price
            trades[-1].amount = amount

            trades[-1].calculate_profit()
            trades[-1].calculate_pnl_pct(trades[-2].amount if len(trades) >= 2 else self.amount, self.leverage)

            self.nr_trades += 1
