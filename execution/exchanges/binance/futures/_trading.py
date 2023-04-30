import logging

import pytz
import os
from datetime import datetime

import django

from database.model.models import Pipeline
from execution.exchanges.binance import BinanceTrader
from execution.service.cron_jobs.save_pipelines_snapshot import save_pipelines_snapshot
from execution.service.helpers.exceptions import SymbolAlreadyTraded, SymbolNotBeingTraded, NoUnits
from execution.service.helpers.exceptions.leverage_setting_fail import LeverageSettingFail
from shared.exchanges import BinanceHandler
from shared.trading import Trader
from execution.service.helpers.decorators import binance_error_handler, handle_order_execution_errors
from shared.utils.decorators.failed_connection import retry_failed_connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


class BinanceFuturesTrader(BinanceTrader):

    def __init__(
        self,
        paper_trading=False
    ):
        BinanceHandler.__init__(self, paper_trading)
        Trader.__init__(self, 0)

        self.paper_trading = paper_trading
        self.symbols = {}
        self.positions = {}
        self.initial_balance = {}
        self.current_balance = {}
        self.units = {}

        self.open_orders = []
        self.filled_orders = []
        self.conn_key = None
        self.exchange = "binance"

    def start_symbol_trading(
        self,
        symbol,
        starting_equity,
        leverage=None,
        header='',
        initial_position=0,
        pipeline_id=None,
        **kwargs
    ):
        if symbol in self.symbols:
            raise SymbolAlreadyTraded(symbol)

        if isinstance(leverage, int):

            return_value = handle_order_execution_errors(
                symbol=symbol,
                trader_instance=self,
                header=header
            )(
                lambda: self.futures_change_leverage(symbol=symbol, leverage=leverage)
            )()

            if return_value and "message" in return_value:
                raise LeverageSettingFail(return_value["message"])

        self._get_symbol_info(symbol)

        self._set_initial_position(symbol, initial_position, header, pipeline_id=pipeline_id, **kwargs)

        self._set_initial_balance(symbol, starting_equity, pipeline_id=pipeline_id, header=header,)

    def stop_symbol_trading(self, symbol, header='', **kwargs):

        if symbol not in self.symbols:
            raise SymbolNotBeingTraded(symbol)

        logging.info(header + f"Closing position for symbol: {symbol}")

        try:
            pipeline_id = kwargs["pipeline_id"]

            save_pipelines_snapshot([self, self], pipeline_id=pipeline_id)

            self.close_pos(symbol, date=datetime.now(tz=pytz.UTC), header=header, **kwargs)
        except NoUnits:
            logging.info(header + "There's no position to be closed.")
            pass

        self.symbols.pop(symbol)

    def close_pos(self, symbol, date=None, row=None, header='', **kwargs):

        if self.units[symbol] == 0:
            raise NoUnits

        if self.units[symbol] < 0:
            self.buy_instrument(symbol, date, row, units=-self.units[symbol], header=header, reducing=True, **kwargs)
        else:
            self.sell_instrument(symbol, date, row, units=self.units[symbol], header=header, reducing=True, **kwargs)

        self._set_position(symbol, 0, previous_position=1, **kwargs)

        self.print_trading_results(header, date, symbol=symbol)

    @retry_failed_connection(num_times=2)
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
        units_factor = 1
        if "reducing" in kwargs:
            kwargs.update({"reduceOnly": True})
            units_factor = 1.2

        units = self._convert_units(amount, units, symbol, units_factor)

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

        order = self._process_order(order, pipeline_id)

        units = float(order["executed_qty"])

        factor = 1 if order_side == self.SIDE_SELL else -1

        self._update_current_balance(
            symbol,
            factor * float(order['cummulative_quote_qty']),
            factor * units,
            pipeline_id
        )

        self.nr_trades += 1

        self.report_trade(order, units, going, header, symbol=symbol)

    def _convert_units(self, amount, units, symbol, units_factor=1):
        price_precision = self.symbols[symbol]["price_precision"]
        quantity_precision = self.symbols[symbol]["quantity_precision"]

        if amount is not None and units is None:
            price = round(float(self.get_symbol_ticker(symbol=symbol)['price']), price_precision)
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

    def _set_initial_balance(self, symbol, starting_equity, pipeline_id, header=''):
        logging.debug(header + f"Updating balance for symbol: {symbol}.")

        self.initial_balance[symbol] = starting_equity
        self.current_balance[symbol] = 0
        self.units[symbol] = 0

        balance, units = self._retrieve_current_balance(pipeline_id)
        self._update_current_balance(symbol, balance, -units, pipeline_id)

        self.print_current_balance(datetime.now(), header=header, symbol=symbol)

    @staticmethod
    def _retrieve_current_balance(pipeline_id):
        pipeline = Pipeline.objects.get(id=pipeline_id)

        return pipeline.balance, pipeline.units

    def _update_current_balance(self, symbol, equity, units, pipeline_id):
        self.current_balance[symbol] += equity
        self.units[symbol] -= units

        Pipeline.objects.filter(id=pipeline_id).update(
            balance=self.current_balance[symbol],
            units=self.units[symbol]
        )

    def _get_symbol_info(self, symbol):

        symbol_obj = self.validate_symbol(symbol)

        self.symbols[symbol] = {
            "base": symbol_obj.base,
            "quote": symbol_obj.quote,
            "price_precision": symbol_obj.price_precision,
            "quantity_precision": symbol_obj.quantity_precision
        }
