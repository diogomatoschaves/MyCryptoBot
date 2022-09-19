import logging
import os
from datetime import datetime

import django
import pytz

from shared.exchanges import BinanceHandler
from shared.trading import Trader

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Position, Trade, Orders


class BinanceTrader(BinanceHandler, Trader):

    AUTO_REPAY = 'AUTO_REPAY'

    def __init__(
        self,
        paper_trading=False
    ):
        BinanceHandler.__init__(self, paper_trading)
        Trader.__init__(self, 0)

        self.positions = {}
        self.exchange = "binance"

    def _set_initial_position(self, symbol, header=''):
        # TODO: Get this value from database?
        logging.debug(header + f"Setting initial position NEUTRAL.")
        self._set_position(symbol, 0)

    def _set_position(self, symbol, position, **kwargs):

        pipeline_id = kwargs.pop("pipeline_id", None)

        self.positions[symbol] = position

        previous_position = kwargs.pop("previous_position", 0)

        new_trade = self._handle_trades(pipeline_id, symbol, previous_position, position)

        if Position.objects.filter(pipeline_id=pipeline_id, symbol=symbol).exists():
            if position == 0:
                Position.objects.filter(
                    pipeline_id=pipeline_id,
                    symbol=symbol
                ).update(
                    position=position,
                    open=False,
                    close_time=datetime.now(tz=pytz.UTC)
                )
            else:
                Position.objects.filter(
                    pipeline_id=pipeline_id,
                    symbol=symbol
                ).update(
                    position=position,
                    open=True,
                    close_time=None
                )
        elif new_trade:
            Position.objects.create(
                position=position,
                symbol_id=symbol,
                exchange_id=self.exchange,
                pipeline_id=pipeline_id,
                paper_trading=self.paper_trading,
                buying_price=new_trade.open_price,
                amount=new_trade.amount,
            )

    def _get_position(self, symbol):
        return self.positions[symbol]

    def _handle_trades(self, pipeline_id, symbol, previous_position, position):

        number_orders = abs(previous_position - position)

        orders = list(
            Orders.objects.filter(
                pipeline_id=pipeline_id,
                symbol_id=symbol
            ).order_by('-transact_time')[:number_orders]
        )

        if len(orders) == 0:
            return None

        if previous_position != 0:

            closing_order = orders.pop(0)

            last_trade = Trade.objects.filter(pipeline_id=pipeline_id, symbol_id=symbol).last()

            if last_trade:
                last_trade.close_price = closing_order.price
                last_trade.close_time = datetime.now(tz=pytz.UTC)
                last_trade.profit_loss = last_trade.side * (last_trade.close_price / last_trade.open_price - 1)
                last_trade.save()

        if position != 0:

            new_order = orders.pop(0)

            # amount = sum([order.executed_qty for order in orders])
            # price = sum([order.price * order.executed_qty for order in orders]) / amount if amount > 0 else 0

            new_trade = Trade.objects.create(
                symbol_id=symbol,
                open_price=new_order.price,
                amount=new_order.executed_qty,
                side=1 if new_order.side == "BUY" else -1,
                exchange_id=self.exchange,
                mock=new_order.mock,
                pipeline_id=pipeline_id
            )

            return new_trade

        return None

    def print_trading_results(self, header, date):
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

    @staticmethod
    def _get_average_order_price(order):
        s = sum([float(fill["price"]) * float(fill["qty"]) for fill in order["fills"]])
        return s / float(order["executedQty"])

    def report_trade(self, order, units, going, header=''):
        logging.debug(order)

        price = order["price"]

        date = datetime.fromtimestamp(order["transactTime"] / 1000).astimezone(pytz.utc)

        logging.info(header + f"" + 100 * "-")
        logging.info(header + f"{date} | {going}")
        logging.info(header + f"units = {units} | price = {price}")
        self.print_current_nav(date, price)
        logging.info(header + f"" + 100 * "-")
