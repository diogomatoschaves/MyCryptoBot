import logging

import pytz
import os
from datetime import datetime

import django
from binance.exceptions import BinanceAPIException

from shared.exchanges import BinanceHandler
from shared.trading import Trader
from shared.utils.decorators.failed_connection import retry_failed_connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol, Orders


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

    def start_symbol_trading(self, symbol):

        if symbol in self.symbols:
            return True

        try:
            symbol_obj = Symbol.objects.get(name=symbol)
            self.symbols[symbol] = {"base": symbol_obj.base.symbol, "quote": symbol_obj.quote.symbol}
        except Symbol.DoesNotExist:
            return False

        trading_account_exists = self._get_assets_info(symbol)

        if not trading_account_exists:
            return False

        self._set_initial_position(symbol)

        self._update_account_status(symbol)

        self._get_symbol_net_equity(symbol)

        self._create_initial_loan(symbol)

        self._get_assets_info(symbol)
        self._update_account_status(symbol)
        self._get_assets_info(symbol)

        self._get_trading_fees(symbol)

        self._get_max_borrow_amount(symbol)

        return True

    def stop_symbol_trading(self, symbol):

        if symbol not in self.symbols:
            return False

        logging.info(f"{symbol}: Closing positions and repaying loans.")

        self.close_pos(symbol, date=datetime.utcnow())

        self.repay_loans(symbol)

        return True

    def buy_instrument(self, symbol, date=None, row=None, units=None, amount=None, **kwargs):
        self._execute_order(
            symbol,
            self.ORDER_TYPE_MARKET,
            self.SIDE_BUY,
            "GOING LONG",
            units=units,
            amount=amount,
            **kwargs
        )

    def sell_instrument(self, symbol, date=None, row=None, units=None, amount=None, **kwargs):
        self._execute_order(
            symbol,
            self.ORDER_TYPE_MARKET,
            self.SIDE_SELL,
            "GOING SHORT",
            units=units,
            amount=amount,
            **kwargs
        )

    def close_pos(self, symbol, date=None, row=None):

        if self.units == 0:
            return

        if self.units < 0:
            self.buy_instrument(symbol, date, row, units=-self.units)
        else:
            self.sell_instrument(symbol, date, row, units=self.units)

        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        self.print_current_balance(symbol, date)

        logging.info(f"{symbol}: " + 100 * "-")
        logging.info(f"{symbol}: {date} | +++ CLOSED FINAL POSITION +++")
        logging.info(f"{symbol}: {date} | net performance (%) = {round(perf, 2)}")
        logging.info(f"{symbol}: {date} | number of trades executed = {self.trades}")
        logging.info(f"{symbol}: " + 100 * "-")

    @retry_failed_connection(num_times=3)
    def _execute_order(
        self,
        symbol,
        order_type,
        order_side,
        going,
        side_effect='MARGIN_BUY',
        units=None,
        amount=None
    ):

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

        self._process_order(order)

        # factor = -1 if order_side == self.SIDE_SELL and amount else 1
        factor = 1 if order_side == self.SIDE_SELL else -1

        units = float(order["executedQty"])

        self.current_balance += factor * float(order['cummulativeQuoteQty'])
        self.units -= factor * units
        # self._update_account_status(factor)

        self.trades += 1

        self.report_trade(order, symbol, units, going)

    def _format_order(self, order):
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
        )

    def _process_order(self, order):

        self.filled_orders.append(order)

        logging.debug(order)

        formatted_order = self._format_order(order)

        Orders.objects.create(**formatted_order)

    def _set_initial_position(self, symbol):
        # TODO: Get this value from database?
        logging.debug(f"{symbol}: Setting initial position NEUTRAL.")
        self._set_position(symbol, 0)

    def _set_position(self, symbol, value):
        self.positions[symbol] = value

    def _get_position(self, symbol):
        return self.positions[symbol]

    @retry_failed_connection(num_times=3)
    def _get_trading_fees(self, symbol):
        logging.debug(f"{symbol}: Getting trading fees.")
        self.trading_fees[symbol] = self.get_trade_fee(symbol=symbol)['tradeFee'][0]

    @retry_failed_connection(num_times=3)
    def _get_assets_info(self, symbol):
        logging.debug(f"{symbol}: Setting asset info.")
        isolated_margin_account_details = self.get_isolated_margin_account()["assets"]

        self.assets_info.update(
            {asset["symbol"]: asset for asset in isolated_margin_account_details if asset["symbol"] == symbol}
        )

        if symbol not in self.assets_info:
            logging.debug(self.assets_info)
            return False

        return True

    def _get_symbol_net_equity(self, symbol):

        logging.debug(f"{symbol}: Getting symbol net equity.")

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
    def _get_max_borrow_amount(self, symbol):
        logging.debug(f"{symbol}: Getting maximum borrow amount.")
        max_borrow_amount = {}

        for key, asset in self.symbols[symbol].items():
            details = self.get_max_margin_loan(asset=asset, isolatedSymbol=symbol)
            max_borrow_amount[asset] = details["borrowLimit"]

        self.max_borrow_amount[symbol] = max_borrow_amount

    @retry_failed_connection(num_times=3)
    def _create_initial_loan(self, symbol):

        logging.debug(f"{symbol}: Creating intial loan.")

        self.max_margin_level = int(float(self.assets_info[symbol]["marginRatio"]))
        if self.margin_level > self.max_margin_level:
            self.margin_level = self.max_margin_level

        # TODO: Suppress message
        try:
            self.sell_instrument(symbol, units=float(self.assets_info[symbol]["baseAsset"]["free"]))
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

            logging.debug(f"{symbol}: Borrowed {amount} of {asset_symbol}.")

    # TODO: Add last order position
    def _update_account_status(self, symbol, factor=1):
        logging.debug(f"{symbol}: Updating isolated account status.")
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

    def report_trade(self, order, symbol, units, going):
        logging.debug(order)

        price = self._get_average_order_price(order)

        date = datetime.fromtimestamp(order["transactTime"] / 1000).astimezone(pytz.utc)

        logging.info(f"{symbol}: " + 100 * "-")
        logging.info(f"{symbol}: {date} | {going}")
        logging.info(f"{symbol} | units = {units} | price = {price}")
        self.print_current_nav(symbol, date, price)
        logging.info(f"{symbol}: " + 100 * "-")
