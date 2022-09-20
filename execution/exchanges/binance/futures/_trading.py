import logging

import pytz
import os
from datetime import datetime

import django
from binance.exceptions import BinanceAPIException

from execution.exchanges.binance import BinanceTrader
from shared.exchanges import BinanceHandler
from shared.trading import Trader
from execution.exchanges.binance.helpers import binance_error_handler
from shared.utils.decorators.failed_connection import retry_failed_connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol


class BinanceFuturesTrader(BinanceTrader):

    def __init__(
        self,
        paper_trading=False
    ):
        BinanceHandler.__init__(self, paper_trading)
        Trader.__init__(self, 0)

        self.paper_trading = paper_trading
        self.max_borrow_amount = {}
        self.symbols = {}
        self.positions = {}
        self.equity = {}

        self.open_orders = []
        self.filled_orders = []
        self.conn_key = None
        self.exchange = "binance"

    # TODO: Make equity mandatory
    def start_symbol_trading(self, symbol, equity=0, leverage=None, header='', **kwargs):

        if symbol in self.symbols:
            return True

        self.equity[symbol] = equity

        if isinstance(leverage, int):
            self.futures_change_leverage(symbol=symbol, leverage=leverage)

        try:
            symbol_obj = Symbol.objects.get(name=symbol)
            self.symbols[symbol] = {"base": symbol_obj.base.symbol, "quote": symbol_obj.quote.symbol}
        except Symbol.DoesNotExist:
            return False

        self._set_initial_position(symbol, header)

        self._set_initial_balance(symbol, equity, header=header)

        return True

    def stop_symbol_trading(self, symbol, header='', **kwargs):

        if symbol not in self.symbols:
            return False

        logging.info(header + f"Closing positions and repaying loans.")

        position_closed = self.close_pos(symbol, date=datetime.now(tz=pytz.UTC), header=header, **kwargs)

        self.symbols.pop(symbol)

        return position_closed

    def close_pos(self, symbol, date=None, row=None, header='', **kwargs):

        if self.units == 0:
            return False

        if self.units < 0:
            self.buy_instrument(symbol, date, row, units=-3*self.units, header=header, reduceOnly=True, **kwargs)
        else:
            self.sell_instrument(symbol, date, row, units=3*self.units, header=header, reduceOnly=True, **kwargs)

        self._set_position(symbol, 0, previous_position=1, **kwargs)

        self.print_trading_results(header, date)

        return True

    @retry_failed_connection(num_times=2)
    @binance_error_handler
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

        pipeline_id = kwargs["pipeline_id"] if "pipeline_id" in kwargs else None

        order = self.futures_create_order(
            symbol=symbol,
            side=order_side,
            type=order_type,
            newOrderRespType='RESULT',
            quantity=units,
            **kwargs
        )

        order["price"] = order["avgPrice"]

        self._process_order(order, pipeline_id)

        factor = 1 if order_side == self.SIDE_SELL else -1

        units = float(order["executedQty"])

        self.current_balance += factor * float(order['cumQuote'])
        self.units -= factor * units

        self.trades += 1

        self.report_trade(order, units, going, header)

    def _format_order(self, order, pipeline_id):
        return dict(
            order_id=order["orderId"],
            client_order_id=order["clientOrderId"],
            symbol_id=order["symbol"],
            transact_time=datetime.fromtimestamp(order["updateTime"] / 1000).astimezone(pytz.utc),
            price=float(order["avgPrice"]),
            original_qty=float(order["origQty"]),
            executed_qty=float(order["executedQty"]),
            cummulative_quote_qty=float(order["cumQty"]),
            status=order["status"],
            type=order["type"],
            side=order["side"],
            mock=self.paper_trading,
            pipeline_id=pipeline_id
        )

    # TODO: Add last order position
    def _set_initial_balance(self, symbol, amount, factor=1, header=''):
        logging.debug(header + f"Updating balance for symbol: {symbol}.")

        balance = amount * factor

        self.current_balance = balance
        self.initial_balance = balance
