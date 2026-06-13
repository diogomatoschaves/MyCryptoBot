import logging
import time
import uuid

import pytz
import os
from datetime import datetime

import django
from binance.exceptions import BinanceAPIException
from django.db import transaction
from requests import ReadTimeout, ConnectionError

from database.model.models import Pipeline
from execution.exchanges.binance import BinanceTrader
from execution.service.blueprints.market_data import filter_balances
from execution.service.cron_jobs.save_pipelines_snapshot import save_pipeline_snapshot
from execution.service.helpers.exceptions import SymbolAlreadyTraded, SymbolNotBeingTraded, NoUnits, NegativeEquity, \
    InsufficientBalance
from execution.service.helpers.exceptions.leverage_setting_fail import LeverageSettingFail
from execution.service.helpers.decorators import handle_order_execution_errors
from shared.utils.decorators.failed_connection import retry_failed_connection
from shared.utils.helpers import get_pipeline_data
from shared.utils.notifier import send_alert

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


class BinanceFuturesTrader(BinanceTrader):

    def __init__(self, paper_trading=False):
        """
        Initializes a BinanceFuturesTrader instance with optional paper trading mode.

        Parameters
        ----------
        paper_trading : bool, optional
            If True, the trader operates in paper trading mode using virtual funds for
            testing strategies without financial risk. Default is False.
        """
        BinanceTrader.__init__(self, paper_trading)

        self.symbols = {}
        self.leverage = {}
        self.position = {}
        self.initial_balance = {}
        self.current_balance = {}
        self.current_equity = {}
        self.units = {}

        self.open_orders = []
        self.filled_orders = []
        self.conn_key = None
        self.exchange = "binance"

    def start_symbol_trading(
        self,
        pipeline_id,
        header='',
        initial_position=0,
        **kwargs
    ):
        """
        Initiates trading for a specific symbol, setting initial parameters including leverage and position.

        Parameters
        ----------
        pipeline_id : int
            The identifier of the trading pipeline configuration.
        header : str, optional
            A header string for logging purposes. Default is an empty string.
        initial_position : int, optional
            The initial trading position for the symbol. Default is 0, indicating no open position.

        Raises
        ------
        SymbolAlreadyTraded
            If an attempt is made to start trading a symbol that is already being traded by this instance.
        """
        pipeline = get_pipeline_data(pipeline_id, return_obj=True)

        symbol = pipeline.symbol.name

        if symbol in self.symbols:
            raise SymbolAlreadyTraded(symbol)

        self._get_symbol_info(symbol)

        self._set_leverage(pipeline, symbol, header)

        self._set_initial_position(symbol, initial_position, header, pipeline_id=pipeline.id, **kwargs)

        self._set_initial_balance(symbol, pipeline, header=header)

        if initial_position == 0:
            self._check_enough_balance(symbol, pipeline)

        self.start_date[symbol] = datetime.now(tz=pytz.utc)

    def stop_symbol_trading(self, pipeline_id, symbol, header='', force=False):
        """
        Stops trading for a specific symbol and optionally forces the closure of any open positions.

        Parameters
        ----------
        pipeline_id : int
            The identifier of the trading pipeline configuration.
        symbol : str
            The trading symbol to stop.
        header : str, optional
            A header string for logging purposes. Default is an empty string.
        force : bool, optional
            If True, forces the closure of any open positions for the symbol. Default is False.

        Raises
        ------
        SymbolNotBeingTraded
            If an attempt is made to stop trading a symbol that is not currently being traded by this instance.
        """
        if force:
            units = self._get_position_amt(symbol)

            if not units:
                self._reset_symbol(symbol)
                return

            self.units[symbol] = units
            self._get_symbol_info(symbol)
        else:
            if symbol not in self.symbols:
                raise SymbolNotBeingTraded(symbol)

        logging.info(header + f"Stopping trading for pipeline {pipeline_id}, symbol {symbol}.")

        try:
            self.close_pos(symbol, date=datetime.now(tz=pytz.UTC), header=header, pipeline_id=pipeline_id)
        except NoUnits:
            logging.info(header + f"There are no units for symbol {symbol}.")
        except KeyError:
            logging.info(header + "There's no position to be closed.")

        self._reset_symbol(symbol)

    def _reset_symbol(self, symbol):
        if symbol in self.symbols:
            self.symbols.pop(symbol)

    def _set_leverage(self, pipeline, symbol, header):
        """
        Sets the leverage for a given symbol based on the pipeline configuration.

        Parameters
        ----------
        pipeline : Pipeline object
            The pipeline configuration object containing leverage settings.
        symbol : str
            The trading symbol for which to set the leverage.
        header : str
            A header string for logging purposes.

        Raises
        ------
        LeverageSettingFail
            If the leverage setting fails due to an API error or invalid configuration.
        """
        return_value = handle_order_execution_errors(
            symbol=symbol,
            trader_instance=self,
            header=header,
            pipeline_id=pipeline.id
        )(
            lambda: self.futures_change_leverage(symbol=symbol, leverage=pipeline.leverage)
        )()

        if return_value and "message" in return_value:
            raise LeverageSettingFail(return_value["message"])

    def _check_enough_balance(self, symbol, pipeline):
        """
        Checks if there is enough balance available for a given symbol based on the
        pipeline's current equity and leverage.

        Parameters
        ----------
        symbol : str
            The trading symbol for which to check the balance.
        pipeline : Pipeline object
            The pipeline configuration object containing equity and leverage settings.

        Raises
        ------
        InsufficientBalance
            If the available balance is less than the required amount based on the
            pipeline's current equity and leverage.
        """

        balances = self.futures_account_balance()
        balance = float(filter_balances(balances, ["USDT"])[0]["availableBalance"])

        if pipeline.current_equity > balance:
            self.symbols.pop(symbol)
            raise InsufficientBalance(round(pipeline.current_equity, 2), round(balance, 2))

    @retry_failed_connection(num_times=2)
    def _get_position_amt(self, symbol):
        """
        Retrieves the current position amount for a given symbol.

        Parameters
        ----------
        symbol : str
            The trading symbol for which to retrieve the position amount.

        Returns
        -------
        float
            The current position amount for the symbol.

        Notes
        -----
        This method uses the futures position information endpoint to fetch the
         current position amount. It is part of the position management functionality.
        """
        positions = self.futures_position_information()
        for symbol_info in positions:
            if symbol_info["symbol"] == symbol:
                return float(symbol_info["positionAmt"])

    def close_pos(self, symbol, date=None, row=None, header='', **kwargs):
        """
        Closes the position for a given symbol, optionally at a specific date and based on additional conditions.

        Parameters
        ----------
        symbol : str
            The trading symbol for which to close the position.
        date : datetime, optional
            The date at which the position should be closed. If not provided, uses the current datetime.
        row : dict, optional
            Additional data that might be required for closing the position. Default is None.
        header : str, optional
            A header string for logging purposes. Default is an empty string.
        kwargs : dict
            Additional keyword arguments that can include 'pipeline_id' for identifying the specific trading pipeline.

        Raises
        ------
        NoUnits
            If there are no units available to close for the given symbol, indicating that there's no open position.
        """

        pipeline_id = kwargs.get('pipeline_id', None)

        logging.info(header + f"Closing position for symbol: {symbol}")

        units = self._convert_units(None, self.units[symbol], symbol)

        if units in [0, -0]:
            raise NoUnits

        if self.units[symbol] < 0:
            self.buy_instrument(
                symbol,
                date,
                row,
                units=-self.units[symbol],
                header=header,
                reducing=True,
                stop_trading=True,
                **kwargs)
        else:
            self.sell_instrument(
                symbol,
                date,
                row,
                units=self.units[symbol],
                header=header,
                reducing=True,
                stop_trading=True,
                **kwargs
            )

        if pipeline_id:
            self._set_position(symbol, 0, previous_position=1, **kwargs)
            self.print_trading_results(pipeline_id=pipeline_id)

    def _place_order_idempotent(self, num_times=2, **order_kwargs):
        """
        Places an order, retrying on connection errors without ever placing it
        twice: the same newClientOrderId is reused across attempts, and after a
        timeout the order status is checked first — the request may have
        reached Binance even though the response was lost.

        Raises the original connection error if the order status cannot be
        confirmed, so callers never mistake an unknown outcome for success.
        """
        symbol = order_kwargs["symbol"]
        client_order_id = order_kwargs["newClientOrderId"]

        retries = 0
        while True:
            try:
                return self.futures_create_order(**order_kwargs)
            except (ConnectionError, ReadTimeout) as conn_error:
                try:
                    return self.futures_get_order(
                        symbol=symbol, origClientOrderId=client_order_id
                    )
                except BinanceAPIException as e:
                    if e.code != -2013:  # anything but ORDER_DOES_NOT_EXIST
                        # outcome unknown - do not re-place
                        send_alert(
                            title="Order outcome UNKNOWN - check Binance manually",
                            body=(
                                f"{symbol}: order {client_order_id} timed out and its "
                                f"status could not be confirmed ({e.message}). VERIFY "
                                f"ON BINANCE whether the order exists before restarting."
                            ),
                            severity="critical",
                            dedup_key=client_order_id,
                        )
                        raise

                retries += 1
                if retries > num_times:
                    send_alert(
                        title="Order placement failed - exchange unreachable",
                        body=(
                            f"{symbol}: order {client_order_id} could not be placed "
                            f"after {num_times} retries ({conn_error!r}). The order "
                            f"was confirmed NOT to exist on Binance."
                        ),
                        severity="critical",
                        dedup_key=client_order_id,
                    )
                    raise conn_error

                logging.debug("Retrying order placement.")
                time.sleep(2 ** (retries - 1))

    def _execute_order(
        self,
        symbol,
        order_type,
        order_side,
        going,
        units,
        amount=None,
        header='',
        **kwargs
    ):
        """
        Executes an order on the Binance Futures market for a given symbol with specified parameters.

        Parameters
        ----------
        symbol : str
            The trading symbol for which to execute the order.
        order_type : str
            The type of order to execute (e.g., MARKET, LIMIT).
        order_side : str
            The side of the order (BUY or SELL).
        going : str
            Indicates the direction of the trade.
        units : float
            The number of units to trade.
        amount : float, optional
            The amount of the order in quote currency. Default is None.
        header : str, optional
            A header string for logging purposes. Default is an empty string.
        kwargs : dict
            Additional keyword arguments including 'reducing', 'stop_trading', and 'pipeline_id'.

        Notes
        -----
        This method is responsible for the actual execution of trades on the Binance Futures market,
        handling order creation and response processing.
        """
        # internal kwargs - never forwarded to the Binance API
        reducing = kwargs.pop('reducing', False)
        stop_trading = kwargs.pop('stop_trading', False)
        pipeline_id = kwargs.pop('pipeline_id', None)

        units = self._convert_units(amount, units, symbol)

        pipeline = get_pipeline_data(pipeline_id, return_obj=True, ignore_exception=True)

        # reused across retries so Binance can deduplicate a re-placed order
        client_order_id = f"{pipeline_id or 'manual'}-{uuid.uuid4().hex}"[:36]

        order = self._place_order_idempotent(
            symbol=symbol,
            side=order_side,
            type=order_type,
            newOrderRespType='RESULT',
            quantity=units,
            newClientOrderId=client_order_id,
            **({"reduceOnly": True} if reducing else {})
        )

        # The exchange has filled the order at this point: everything below is
        # bookkeeping, written in one transaction so local records are
        # all-or-nothing, and applied to in-memory state only after commit so
        # that memory always matches the database.
        def bookkeeping():
            with transaction.atomic():
                formatted_order = self._process_order(order, pipeline_id)

                state = None
                if pipeline:
                    factor = 1 if order_side == self.SIDE_SELL else -1
                    units_filled = float(formatted_order["executed_qty"])

                    state = self._compute_net_value(
                        symbol,
                        factor * float(formatted_order['cummulative_quote_qty']),
                        factor * units_filled,
                        pipeline,
                        reducing
                    )
                    self._persist_net_value(pipeline, state, reducing)

                return formatted_order, state

        formatted_order, new_state = self._run_bookkeeping(
            bookkeeping,
            pipeline_id=pipeline_id,
            symbol=symbol,
            detail=f"order {client_order_id} ({order_side} {units} {symbol})"
        )

        units = float(formatted_order["executed_qty"])

        self.nr_trades += 1

        if pipeline:
            self._apply_net_value(symbol, new_state)

            self.report_trade(formatted_order, units, going, header, symbol=symbol)

            self._check_negative_equity(symbol, reducing=reducing, stop_trading=stop_trading)

    def _convert_units(self, amount, units, symbol, units_factor=1):
        """
        Converts the amount specified in quote currency to units of the base currency or adjusts units
        based on a factor.

        Parameters
        ----------
        amount : float, optional
            The amount to convert to units. Default is None, which means the conversion is not based on an amount.
        units : float
            The number of units, which can be adjusted by the units_factor if amount is None.
        symbol : str
            The trading symbol for which to perform the conversion.
        units_factor : float, optional
            A factor by which to adjust the units. Default is 1.

        Returns
        -------
        float
            The converted or adjusted number of units.

        Notes
        -----
        This method is used for unit conversions necessary for order execution, accommodating both
        amount-based and units-based trade specifications.
        """
        price_precision = self.symbols[symbol]["price_precision"]
        quantity_precision = self.symbols[symbol]["quantity_precision"]

        if amount is not None and units is None:
            price = round(float(self.futures_symbol_ticker(symbol=symbol)['price']), price_precision)
            units = round(amount / price * units_factor, quantity_precision)

            # in case units are negative
            units = max(0, units)

            return units
        else:
            return round(units * units_factor, quantity_precision)

    def _format_order(self, order, pipeline_id):
        return dict(
            order_id=order["orderId"],
            client_order_id=order["clientOrderId"],
            symbol_id=order["symbol"],
            transact_time=datetime.fromtimestamp(order["updateTime"] / 1000).astimezone(pytz.utc),
            price=float(order["avgPrice"]),
            original_qty=float(order["origQty"]),
            executed_qty=float(order["executedQty"]),
            cummulative_quote_qty=float(order["cumQuote"]),
            status=order["status"],
            type=order["type"],
            side=order["side"],
            mock=self.paper_trading,
            pipeline_id=pipeline_id
        )

    def _set_initial_balance(self, symbol, pipeline, header=''):
        """
        Sets the initial balance, units, and equity for a specified trading
        symbol based on the pipeline configuration.

        Parameters
        ----------
        symbol : str
            The trading symbol for which to set the initial balance and units.
        pipeline : Pipeline object
            The trading pipeline configuration object, containing current equity and leverage settings.
        header : str
            An optional header string for logging purposes.

        Notes
        -----
        This method initializes the trading state for the symbol, including setting
        the initial balance based on the pipeline's current equity and leverage.
        It logs the initial balance setup for the specified symbol.
        """
        logging.debug(header + f"Updating balance for symbol: {symbol}.")

        self.initial_balance[symbol] = pipeline.current_equity * pipeline.leverage
        self.current_balance[symbol] = 0
        self.units[symbol] = 0
        self.current_equity[symbol] = pipeline.current_equity

        self._update_net_value(symbol, pipeline.balance, -pipeline.units, pipeline)

        self.print_current_balance(datetime.now(), header=header, symbol=symbol)

    def _compute_net_value(self, symbol, balance, units, pipeline, reducing=False):
        """
        Computes the new net value, units, and balances for a specified symbol
        without mutating any state.

        Pure on purpose: the result is first persisted to the database inside
        a transaction and only applied to the in-memory trading state after
        the commit succeeds, so memory and database can never diverge.

        Returns
        -------
        dict
            The new `units`, `balance` and `equity` values for the symbol.
        """
        new_units = self.units[symbol] - units
        new_balance = self.current_balance[symbol] + balance
        new_equity = self.current_equity[symbol]

        # Correction of balance if leverage is different from 1
        if reducing:
            initial_balance = new_equity * pipeline.leverage
            pnl = new_balance - initial_balance

            new_equity = new_equity + pnl
            new_balance = new_equity * pipeline.leverage

        return {"units": new_units, "balance": new_balance, "equity": new_equity}

    def _persist_net_value(self, pipeline, state, reducing):
        """
        Writes the computed net value to the pipeline row. Must be called
        inside a transaction; the snapshot is deferred to after the commit
        so it only ever records committed state.
        """
        pipeline.balance = state["balance"]
        pipeline.units = state["units"]
        pipeline.current_equity = state["equity"]
        pipeline.save(update_fields=["balance", "units", "current_equity"])

        if reducing:
            transaction.on_commit(lambda: save_pipeline_snapshot(pipeline_id=pipeline.id))

    def _apply_net_value(self, symbol, state):
        """Applies a computed net value to the in-memory trading state."""
        self.units[symbol] = state["units"]
        self.current_balance[symbol] = state["balance"]
        self.current_equity[symbol] = state["equity"]

    def _update_net_value(self, symbol, balance, units, pipeline, reducing=False):
        """
        Computes, persists and applies a net value update in one step. Used
        outside the order path (e.g. when initializing a symbol's balance);
        the order path runs the same pieces inside its own transaction.
        """
        state = self._compute_net_value(symbol, balance, units, pipeline, reducing)

        with transaction.atomic():
            self._persist_net_value(pipeline, state, reducing)

        self._apply_net_value(symbol, state)

    def _get_symbol_info(self, symbol):
        """
        Retrieves and stores trading symbol information, including base asset,
        quote asset, price precision, and quantity precision.

        Parameters
        ----------
        symbol : str
            The trading symbol for which to retrieve and store information.

        Notes
        -----
        This method uses the `validate_symbol` method (expected to be implemented
        within the `BinanceTrader` or an equivalent class) to fetch symbol information from the exchange.
        The information is stored in the `symbols` dictionary attribute, indexed by the symbol string.

        The `symbols` dictionary is essential for ensuring that orders are placed with the
        correct precision and for handling asset conversions and calculations accurately.
        """

        symbol_obj = self.validate_symbol(symbol)

        self.symbols[symbol] = {
            "base": symbol_obj.base,
            "quote": symbol_obj.quote,
            "price_precision": symbol_obj.price_precision,
            "quantity_precision": symbol_obj.quantity_precision
        }

    def _check_negative_equity(self, symbol, reducing, stop_trading=False):
        """
        Checks for negative equity for a given symbol and raises an exception if found.

        Parameters
        ----------
        symbol : str
            The trading symbol to check for negative equity.
        reducing : bool
            Indicates whether the equity check is performed after reducing a position.
        stop_trading : bool, optional
            If True, stops trading if negative equity is detected. Default is False.

        Raises
        ------
        NegativeEquity
            If negative equity is detected for the symbol.
        """
        if reducing and not stop_trading:
            if self.current_balance[symbol] < 0:
                raise NegativeEquity(self.current_balance[symbol])
