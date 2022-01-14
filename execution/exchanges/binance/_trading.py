import logging

import pytz
import os
from datetime import datetime

import django
from binance.exceptions import BinanceAPIException

from shared.exchanges import BinanceHandler
from shared.trading import Trader
from execution.exchanges.binance.helpers import binance_error_handler
from shared.utils.decorators.failed_connection import retry_failed_connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Orders, Position


class BinanceTrader(BinanceHandler, Trader):

    AUTO_REPAY = 'AUTO_REPAY'

    def __init__(
        self,
        margin_level=3,
        paper_trading=False
    ):
        BinanceHandler.__init__(self, paper_trading)
        Trader.__init__(self, 0)

        self.paper_trading = paper_trading
        self.margin_level = margin_level
        self.account_equity = {}
        self.assets_info = {}
        self.trading_fees = {}
        self.max_borrow_amount = {}
        self.symbols = {}
        self.positions = {}

        self.open_orders = []
        self.filled_orders = []
        self.conn_key = None
        self.exchange = 'binance'

    def start_symbol_trading(self, symbol, header='', **kwargs):

        if symbol in self.symbols:
            return True

        try:
            symbol_obj = Symbol.objects.get(name=symbol)
            self.symbols[symbol] = {"base": symbol_obj.base.symbol, "quote": symbol_obj.quote.symbol}
        except Symbol.DoesNotExist:
            return False

        trading_account_exists = self._get_assets_info(symbol, header)

        if not trading_account_exists:
            return False

        self._set_initial_position(symbol, header)

        self._update_account_status(symbol, header=header)

        self._get_symbol_net_equity(symbol, header)

        self._create_initial_loan(symbol, header, **kwargs)

        self._get_assets_info(symbol, header)
        self._update_account_status(symbol, header=header)
        self._get_assets_info(symbol, header)

        self._get_trading_fees(symbol, header)

        self._get_max_borrow_amount(symbol, header)

        return True

    def stop_symbol_trading(self, symbol, header='', **kwargs):

        if symbol not in self.symbols:
            return False

        logging.info(header + f"Closing positions and repaying loans.")

        position_closed = self.close_pos(symbol, date=datetime.utcnow(), header=header, **kwargs)

        self.repay_loans(symbol)

        return position_closed

    def buy_instrument(self, symbol, date=None, row=None, units=None, amount=None, header='', **kwargs):
        self._execute_order(
            symbol,
            self.ORDER_TYPE_MARKET,
            self.SIDE_BUY,
            "GOING LONG",
            units=units,
            amount=amount,
            header=header,
            **kwargs
        )

    def sell_instrument(self, symbol, date=None, row=None, units=None, amount=None, header='', **kwargs):
        self._execute_order(
            symbol,
            self.ORDER_TYPE_MARKET,
            self.SIDE_SELL,
            "GOING SHORT",
            units=units,
            amount=amount,
            header=header,
            **kwargs
        )

    def close_pos(self, symbol, date=None, row=None, header='', **kwargs):

        if self.units == 0:
            return False

        if self.units < 0:
            self.buy_instrument(symbol, date, row, units=-self.units, header=header, **kwargs)
        else:
            self.sell_instrument(symbol, date, row, units=self.units, header=header, **kwargs)

        self._set_position(symbol, 0, **kwargs)

        try:
            perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        except ZeroDivisionError:
            perf = 0

        self.print_current_balance(date, header=header)
        
        header = header

        logging.info(header + f"" + 100 * "-")
        logging.info(header + f"{date} | +++ CLOSED FINAL POSITION +++")
        logging.info(header + f"{date} | net performance (%) = {round(perf, 2)}")
        logging.info(header + f"{date} | number of trades executed = {self.trades}")
        logging.info(header + f"" + 100 * "-")

        return True

    @retry_failed_connection(num_times=2)
    @binance_error_handler
    def _execute_order(
        self,
        symbol,
        order_type,
        order_side,
        going,
        side_effect='MARGIN_BUY',
        units=None,
        amount=None,
        header='',
        **kwargs
    ):

        pipeline_id = kwargs["pipeline_id"] if "pipeline_id" in kwargs else None

        kwargs = self._get_order_kwargs(units, amount)

        if kwargs.get("quantity") == 0 or kwargs.get("quoteOrderQty") == 0:
            return

        order = self.create_margin_order(
            symbol=symbol,
            side=order_side,
            type=order_type,
            newOrderRespType='FULL',
            isIsolated=True,
            sideEffectType=side_effect,
            **kwargs
        )

        order["price"] = self._get_average_order_price(order)

        self._process_order(order, pipeline_id)

        # factor = -1 if order_side == self.SIDE_SELL and amount else 1
        factor = 1 if order_side == self.SIDE_SELL else -1

        units = float(order["executedQty"])

        self.current_balance += factor * float(order['cummulativeQuoteQty'])
        self.units -= factor * units
        # self._update_account_status(factor)

        self.trades += 1

        self.report_trade(order, symbol, units, going, header)

    def _format_order(self, order, pipeline_id):
        return dict(
            order_id=order["orderId"],
            client_order_id=order["clientOrderId"],
            symbol_id=order["symbol"],
            transact_time=datetime.fromtimestamp(order["transactTime"] / 1000).astimezone(pytz.utc),
            price=float(order["price"]),
            original_qty=float(order["origQty"]),
            executed_qty=float(order["executedQty"]),
            cummulative_quote_qty=float(order["cummulativeQuoteQty"]),
            status=order["status"],
            type=order["type"],
            side=order["side"],
            is_isolated=order["isIsolated"],
            mock=self.paper_trading,
            pipeline_id=pipeline_id
        )

    def _process_order(self, order, pipeline_id):

        self.filled_orders.append(order)

        logging.debug(order)

        formatted_order = self._format_order(order, pipeline_id)

        Orders.objects.create(**formatted_order)

    def _set_initial_position(self, symbol, header=''):
        # TODO: Get this value from database?
        logging.debug(header + f"Setting initial position NEUTRAL.")
        self._set_position(symbol, 0)

    def _set_position(self, symbol, value, **kwargs):

        pipeline_id = kwargs.pop("pipeline_id", None)

        self.positions[symbol] = value

        qs = Orders.objects.filter(pipeline_id=pipeline_id, symbol_id=symbol).order_by('-transact_time')[:2]

        if len(qs) >= 2 and \
                qs[0].pipeline_id == qs[1].pipeline_id and \
                qs[0].symbol == qs[1].symbol and \
                qs[0].side == qs[1].side:

            amount = qs[0].executed_qty + qs[1].executed_qty
            price = (qs[0].price + qs[1].price) / amount
        elif len(qs) >= 1:
            amount = qs[0].executed_qty
            price = qs[0].price
        else:
            return

        if Position.objects.filter(pipeline_id=pipeline_id, symbol=symbol).exists():
            if value == 0:
                Position.objects.filter(
                    pipeline_id=pipeline_id,
                    symbol=symbol
                ).update(
                    position=value,
                    open=False,
                    close_time=datetime.utcnow()
                )
            else:
                Position.objects.filter(
                    pipeline_id=pipeline_id,
                    symbol=symbol
                ).update(
                    position=value,
                    open=True,
                    close_time=None
                )
        else:
            Position.objects.create(
                position=value,
                symbol_id=symbol,
                exchange_id=self.exchange,
                pipeline_id=pipeline_id,
                paper_trading=self.paper_trading,
                buying_price=price,
                amount=amount,
            )

    def _get_position(self, symbol):
        return self.positions[symbol]

    @retry_failed_connection(num_times=3)
    def _get_trading_fees(self, symbol, header=''):
        logging.debug(header + f"Getting trading fees.")
        self.trading_fees[symbol] = self.get_trade_fee(symbol=symbol)['tradeFee'][0]

    @retry_failed_connection(num_times=3)
    def _get_assets_info(self, symbol, header=''):
        logging.debug(header + f"Setting asset info.")
        isolated_margin_account_details = self.get_isolated_margin_account()["assets"]

        self.assets_info.update(
            {asset["symbol"]: asset for asset in isolated_margin_account_details if asset["symbol"] == symbol}
        )

        if symbol not in self.assets_info:
            logging.debug(self.assets_info)
            return False

        return True

    def _get_symbol_net_equity(self, symbol, header=''):

        logging.debug(header + f"Getting symbol net equity.")

        quote_amount = float(self.assets_info[symbol]["quoteAsset"]["netAsset"])
        quote_amount += float(self.assets_info[symbol]["baseAsset"]["netAsset"]) * \
                        float(self.assets_info[symbol]["indexPrice"])

        base_amount = float(self.assets_info[symbol]["baseAsset"]["netAsset"])
        base_amount += float(self.assets_info[symbol]["quoteAsset"]["netAsset"]) / \
                       float(self.assets_info[symbol]["indexPrice"])

        self.account_equity[symbol] = {
            self.symbols[symbol]["quote"]: quote_amount,
            self.symbols[symbol]["base"]: base_amount,
        }

    @retry_failed_connection(num_times=3)
    def _get_max_borrow_amount(self, symbol, header=''):
        logging.debug(header + f"Getting maximum borrow amount.")
        max_borrow_amount = {}

        for key, asset in self.symbols[symbol].items():
            details = self.get_max_margin_loan(asset=asset, isolatedSymbol=symbol)
            max_borrow_amount[asset] = details["borrowLimit"]

        self.max_borrow_amount[symbol] = max_borrow_amount

    @retry_failed_connection(num_times=3)
    def _create_initial_loan(self, symbol, header='', **kwargs):

        logging.debug(header + f"Creating intial loan.")

        self.max_margin_level = int(float(self.assets_info[symbol]["marginRatio"]))
        if self.margin_level > self.max_margin_level:
            self.margin_level = self.max_margin_level

        # TODO: Suppress message
        try:
            self.sell_instrument(symbol, units=float(self.assets_info[symbol]["baseAsset"]["free"]), **kwargs)
        except BinanceAPIException:
            pass

        asset_details = [
            {
                "asset": self.symbols[symbol]["quote"],
                "free_amount": float(self.assets_info[symbol]["quoteAsset"]["free"]),
                "net_amount": float(self.assets_info[symbol]["quoteAsset"]["netAsset"]),
                "borrowed_amount": float(self.assets_info[symbol]["quoteAsset"]["borrowed"])
            }
        ]

        for asset in asset_details:
            asset_symbol = asset["asset"]

            total_amount = self.margin_level * self.account_equity[symbol][asset_symbol]

            amount = total_amount / 2 - (asset["net_amount"] + asset["borrowed_amount"])

            if amount <= 0:
                continue

            self.create_margin_loan(asset=asset_symbol, amount=amount, isIsolated=True, symbol=symbol)

            logging.debug(header + f"Borrowed {amount} of {asset_symbol}.")

    # TODO: Add last order position
    def _update_account_status(self, symbol, factor=1, header=''):
        logging.debug(header + f"Updating isolated account status.")
        self.current_balance = float(self.assets_info[symbol]["quoteAsset"]["free"])
        self.units = float(self.assets_info[symbol]["baseAsset"]["free"]) * factor

    @staticmethod
    def _get_order_kwargs(units, amount):
        kwargs = {}
        if units:
            kwargs["quantity"] = round(units, 6)
        elif amount:
            kwargs["quoteOrderQty"] = amount

        return kwargs

    @staticmethod
    def _get_average_order_price(order):
        s = sum([float(fill["price"]) * float(fill["qty"]) for fill in order["fills"]])
        return s / float(order["executedQty"])

    @retry_failed_connection(num_times=3)
    def repay_loans(self, symbol):
        for key, asset in self.symbols[symbol].items():
            try:
                self.repay_margin_loan(
                    asset=asset,
                    amount=self.max_borrow_amount[symbol][asset],
                    isIsolated='TRUE',
                    symbol=symbol
                )
            except BinanceAPIException:
                pass

    def report_trade(self, order, symbol, units, going, header=''):
        logging.debug(order)

        price = self._get_average_order_price(order)

        date = datetime.fromtimestamp(order["transactTime"] / 1000).astimezone(pytz.utc)

        logging.info(header + f"" + 100 * "-")
        logging.info(header + f"{date} | {going}")
        logging.info(header + f"units = {units} | price = {price}")
        self.print_current_nav(date, price)
        logging.info(header + f"" + 100 * "-")
