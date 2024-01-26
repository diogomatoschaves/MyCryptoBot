import logging

import pytz
import os
from datetime import datetime

import django

from database.model.models import Pipeline
from execution.exchanges.binance import BinanceTrader
from execution.service.blueprints.market_data import filter_balances
from execution.service.cron_jobs.save_pipelines_snapshot import save_pipelines_snapshot
from execution.service.helpers.exceptions import SymbolAlreadyTraded, SymbolNotBeingTraded, NoUnits, NegativeEquity
from execution.service.helpers.exceptions.leverage_setting_fail import LeverageSettingFail
from execution.service.helpers.decorators import handle_order_execution_errors, binance_error_handler
from shared.utils.decorators.failed_connection import retry_failed_connection
from shared.utils.helpers import get_pipeline_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


class BinanceFuturesTrader(BinanceTrader):

    def __init__(
        self,
        paper_trading=False
    ):
        BinanceTrader.__init__(self, paper_trading)

        self.symbols = {}
        self.leverage = {}
        self.positions = {}
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
        symbol,
        current_equity,
        pipeline_id,
        leverage,
        header='',
        initial_position=0,
        **kwargs
    ):
        if symbol in self.symbols:
            raise SymbolAlreadyTraded(symbol)

        if isinstance(leverage, int):

            return_value = handle_order_execution_errors(
                symbol=symbol,
                trader_instance=self,
                header=header,
                pipeline_id=pipeline_id
            )(
                lambda: self.futures_change_leverage(symbol=symbol, leverage=leverage)
            )()

            if return_value and "message" in return_value:
                raise LeverageSettingFail(return_value["message"])

        pipeline = get_pipeline_data(pipeline_id, return_obj=True)

        self._get_symbol_info(symbol)

        self._set_leverage(symbol, leverage)

        self._set_initial_position(symbol, initial_position, header, pipeline_id=pipeline.id, **kwargs)

        self._set_initial_balance(symbol, current_equity, pipeline, header=header)

    def stop_symbol_trading(self, symbol, header='', **kwargs):

        if symbol not in self.symbols:
            raise SymbolNotBeingTraded(symbol)

        logging.info(header + f"Stopping trading.")

        try:
            pipeline_id = kwargs["pipeline_id"]

            self.close_pipeline(pipeline_id)

            save_pipelines_snapshot([self, self], pipeline_id=pipeline_id)

            self.close_pos(symbol, date=datetime.now(tz=pytz.UTC), header=header, **kwargs)
        except NoUnits:
            logging.info(header + "There's no position to be closed.")

        self.symbols.pop(symbol)

    def close_pos(self, symbol, date=None, row=None, header='', **kwargs):

        logging.info(header + f"Closing position for symbol: {symbol}")

        units = self._convert_units(None, self.units[symbol], symbol)

        if units in [0, -0]:
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
        reducing = "reducing" in kwargs

        units = self._convert_units(amount, units, symbol)

        print("units: ", units)

        pipeline_id = kwargs["pipeline_id"] if "pipeline_id" in kwargs else None
        pipeline = Pipeline.objects.get(id=pipeline_id)

        order = self.futures_create_order(
            symbol=symbol,
            side=order_side,
            type=order_type,
            newOrderRespType='RESULT',
            quantity=units,
            **kwargs
        )

        order = self._process_order(order, pipeline.id)

        units = float(order["executed_qty"])

        factor = 1 if order_side == self.SIDE_SELL else -1

        self.nr_trades += 1

        self._update_net_value(
            symbol,
            factor * float(order['cummulative_quote_qty']),
            factor * units,
            pipeline,
            reducing
        )

        self.report_trade(order, units, going, header, symbol=symbol)

        self.check_negative_equity(symbol, reducing=reducing)

    @binance_error_handler(num_times=2)
    def _convert_units(self, amount, units, symbol, units_factor=1):
        price_precision = self.symbols[symbol]["price_precision"]
        quantity_precision = self.symbols[symbol]["quantity_precision"]

        if amount is not None and units is None:
            price = round(float(self.futures_symbol_ticker(symbol=symbol)['price']), price_precision)
            units = round(amount / price * units_factor, quantity_precision)

            print(price,  amount, units)

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

    def _set_initial_balance(self, symbol, initial_balance, pipeline, header=''):
        logging.debug(header + f"Updating balance for symbol: {symbol}.")

        self.initial_balance[symbol] = initial_balance
        self.current_balance[symbol] = 0
        self.units[symbol] = 0
        self.current_equity[symbol] = pipeline.current_equity

        self._update_net_value(symbol, pipeline.balance, -pipeline.units, pipeline)

        self.print_current_balance(datetime.now(), header=header, symbol=symbol)

    def _set_leverage(self, symbol, leverage):
        self.leverage[symbol] = leverage

    def _update_net_value(self, symbol, balance, units, pipeline, reducing=False):

        self.units[symbol] -= units
        self.current_balance[symbol] += balance

        print("updated balance, units: ", self.current_balance[symbol], self.units[symbol])
        print("balance, units: ", self.current_balance[symbol], self.units[symbol])

        # Correction of balance if leverage is different from 1
        if reducing:
            initial_balance = self.current_equity[symbol] * pipeline.leverage
            pnl = self.current_balance[symbol] - initial_balance

            print("initial_balance, pnl: ", initial_balance, pnl)

            self.current_equity[symbol] = self.current_equity[symbol] + pnl
            self.current_balance[symbol] = self.current_equity[symbol] * pipeline.leverage

            print("current equity: ", self.current_equity[symbol])
            print("current balance: ", self.current_balance[symbol])

        pipeline.balance = self.current_balance[symbol]
        pipeline.units = self.units[symbol]
        pipeline.current_equity = self.current_equity[symbol]
        pipeline.save()

    def _get_symbol_info(self, symbol):

        symbol_obj = self.validate_symbol(symbol)

        self.symbols[symbol] = {
            "base": symbol_obj.base,
            "quote": symbol_obj.quote,
            "price_precision": symbol_obj.price_precision,
            "quantity_precision": symbol_obj.quantity_precision
        }

    @staticmethod
    def close_pipeline(pipeline_id):
        Pipeline.objects.filter(id=pipeline_id).update(active=False, open_time=None)

    def check_negative_equity(self, symbol, reducing):
        if reducing:
            if self.current_balance[symbol] < 0:
                raise NegativeEquity(self.current_balance[symbol])
