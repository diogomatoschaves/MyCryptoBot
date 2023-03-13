import numpy as np

from model.backtesting._mixin import BacktestMixin
from model.backtesting.helpers import Trade
from shared.trading import Trader


class IterativeBacktester(BacktestMixin, Trader):
    """
    A class for backtesting trading strategies iteratively using historical data.
    """

    def __init__(self, strategy, symbol=None, amount=1000, trading_costs=0):
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

        BacktestMixin.__init__(self, symbol, amount, trading_costs)
        Trader.__init__(self, amount)

        self.strategy = strategy
        self.strategy.symbol = symbol

        self.positions_lst = []
        self.equity = [self.amount]
        self.returns = []
        self.strategy_returns = []
        self.strategy_returns_tc = []
        self.positions = {
            symbol: 0
        }

    def __repr__(self):
        """
        Returns a string representation of the trading strategy.
        """
        return self.strategy.__repr__()

    def _set_position(self, symbol, value, **kwargs):
        """
        Sets the position for the given symbol.

        Parameters
        ----------
        symbol : str
            The trading symbol.
        value : int
            The position value.
        """
        self.positions[symbol] = value

    def _get_position(self, symbol):
        """
        Gets the position for the given symbol.

        Parameters
        ----------
        symbol : str
            The trading symbol.

        Returns
        -------
        float
            The position value.
        """
        return self.positions[symbol]

    def _reset_object(self):
        """
        Resets the object attributes to their initial values.
        """
        self._set_position(self.symbol, 0)  # initial neutral position
        self.equity = [self.amount]
        self.strategy_returns = []
        self.strategy_returns_tc = []
        self.positions_lst = [0]
        self.nr_trades = 0
        self.current_balance = self.initial_balance  # reset initial capital

    def _calculate_positions(self, data):
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
        data["position"] = self.positions_lst
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
        price = row[self.price_col]

        return price

    def _test_strategy(self, params=None, print_results=True, plot_results=True, plot_positions=False):
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
        plot_positions : bool, optional
            Flag for whether to plot the position markers on the results plot.

        Returns
        -------
        dict
            Dictionary containing the performance metrics of the backtest.

        """
        self.set_parameters(params)
        self._reset_object()

        # nice printout
        print("-" * 75)
        print(self._get_test_title())
        print("-" * 75)

        data = self._get_data().dropna().copy()

        processed_data = self._iterative_backtest(data, print_results)

        results, nr_trades, perf, outperf = self._evaluate_backtest(processed_data)

        self._print_results(results, print_results)

        self.plot_results(self.processed_data, plot_results, plot_positions)

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
                self.close_pos(self.symbol, timestamp, row)  # close position at the last bar
                self._set_position(self.symbol, 0)

            new_position = self._get_position(self.symbol)

            self.positions_lst.append(new_position)

            trades = np.abs(new_position - previous_position)

            self.strategy_returns.append(row[self.returns_col] * previous_position)
            self.strategy_returns_tc.append(self.strategy_returns[-1] - trades * self.tc)

            self.equity.append(self._get_net_value(row))

        return data

    def _evaluate_backtest(self, processed_data):

        processed_data["position"] = self.positions_lst[:-1]
        processed_data.loc[processed_data.index[0], "position"] = self.positions_lst[1]
        processed_data["strategy_returns"] = self.strategy_returns
        processed_data["strategy_returns_tc"] = self.strategy_returns_tc

        processed_data["accumulated_returns"] = processed_data[self.returns_col].cumsum().apply(np.exp)
        processed_data["accumulated_strategy_returns"] = processed_data["strategy_returns"].cumsum().apply(np.exp)
        processed_data["accumulated_strategy_returns_tc"] = processed_data["strategy_returns_tc"].cumsum().apply(np.exp)

        processed_data.dropna(inplace=True)

        self.processed_data = processed_data

        returns = [np.log(trade.exit_price / trade.entry_price) * trade.direction for trade in self.trades]
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
            amount = units * price_tc

        self.current_balance -= amount
        self.units += units

        self._handle_trade(self.trades, open_trade, date, price_tc, units, 1)

        if print_results:
            print(f"{date} |  Buying {round(units, 4)} {self.symbol} for {round(price, 5)}")

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

        self._handle_trade(self.trades, open_trade, date, price_tc, units, -1)

        if print_results:
            print(f"{date} |  Selling {round(units, 4)} {self.symbol} for {round(price, 5)}")

    def close_pos(self, symbol, date=None, row=None, header='', **kwargs):
        """
        Closes the position of the specified instrument at the given date or row. If the number of units is less than or equal to
        zero, it buys the instrument to close the position, otherwise it sells it. It then calculates the performance of the
        trading account, updates the `current_balance`, `trades` and `units` attributes accordingly, and prints a message
        showing the current balance, net performance and number of trades executed.

        Parameters
        ----------
        symbol : str
            The symbol of the instrument to close the position for.
        date : str or None, optional
            The date to close the position at, formatted as 'YYYY-MM-DD'. If None, row must be specified instead.
        row : int or None, optional
            The row index to close the position at. If None, date must be specified instead.
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
        print(75 * "-")
        print("{} |  +++ CLOSING FINAL POSITION +++".format(date))

        if self.units <= 0:
            self.buy_instrument(symbol, date, row, open_trade=False, units=-self.units)
        else:
            self.sell_instrument(symbol, date, row, open_trade=False, units=self.units)

        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        self.print_current_balance(date)

        print("{} |  net performance (%) = {}".format(date, round(perf, 2)))
        print("{} |  number of trades executed = {}".format(date, self.nr_trades))
        print(75 * "-")

    def _handle_trade(self, trades, open_trade, date, price, units, direction, update_trade_counter=True):
        if open_trade:
            trades.append(Trade(date, None, price, None, units, direction, None, None))
        else:
            trades[-1].exit_date = date
            trades[-1].exit_price = price

            trades[-1].calculate_profit()

            if update_trade_counter:
                self.nr_trades += 1

    def plot_data(self, cols=None):
        """
        Plots the data of the specified columns in the `data` attribute. If `cols` is not provided, it defaults to "close".

        Plot data for the specified columns.

        Parameters
        ----------
        cols : str or list of str,
            The column(s) to plot. If not provided, it defaults to "close".

        Returns
        -------
        None
        """

        if cols is None:
            cols = "close"
        self.data[cols].plot(figsize=(12, 8), title='BTC/USD')
