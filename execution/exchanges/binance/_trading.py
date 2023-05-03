import logging
import os
from datetime import datetime

import django
import pytz

from shared.exchanges import BinanceHandler
from shared.trading import Trader

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Position, Trade, Orders, Pipeline


class BinanceTrader(BinanceHandler, Trader):

    AUTO_REPAY = 'AUTO_REPAY'

    def __init__(
        self,
        paper_trading=False
    ):
        BinanceHandler.__init__(self, paper_trading)
        Trader.__init__(self, 0)

        self.positions = {}
        self.filled_orders = []
        self.exchange = "binance"

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

    def _set_initial_position(self, symbol, initial_position, header='', **kwargs):

        position = "NEUTRAL" if initial_position == 0 else "LONG" if initial_position == 1 else "SHORT"

        logging.debug(header + f"Setting initial position {position}.")

        self._set_position(symbol, initial_position, previous_position=initial_position, **kwargs)

    def _set_position(self, symbol, position, **kwargs):

        pipeline_id = kwargs.pop("pipeline_id", None)

        self.positions[symbol] = position

        previous_position = kwargs.pop("previous_position", 0)

        new_trade = self._handle_trades(pipeline_id, symbol, previous_position, position)

        if Position.objects.filter(pipeline_id=pipeline_id).exists():
            if position == 0:
                Position.objects.filter(
                    pipeline_id=pipeline_id,
                ).update(
                    position=position,
                    open=False,
                    amount=None,
                    buying_price=None,
                    open_time=None,
                )
            else:
                if new_trade:
                    Position.objects.filter(
                        pipeline_id=pipeline_id,
                    ).update(
                        position=position,
                        open=True,
                        open_time=datetime.now(tz=pytz.UTC),
                        buying_price=new_trade.open_price,
                        amount=new_trade.amount
                    )
        else:
            Position.objects.create(
                position=position,
                symbol_id=symbol,
                exchange_id=self.exchange,
                pipeline_id=pipeline_id,
                paper_trading=self.paper_trading,
                buying_price=new_trade.open_price if new_trade else None,
                amount=new_trade.amount if new_trade else None,
            )

    def _format_order(self, order, pipeline_id):
        raise NotImplementedError

    def _execute_order(self, symbol, order_type, order_side, going, units, amount, header, **kwargs):
        raise NotImplementedError

    def _process_order(self, order, pipeline_id):

        self.filled_orders.append(order)

        logging.debug(order)

        formatted_order = self._format_order(order, pipeline_id)

        order_created = Orders.objects.create(**formatted_order)

        return formatted_order

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
                last_trade.profit_loss = last_trade.get_profit_loss()
                last_trade.save()

        if position != 0:

            new_order = orders.pop(0)

            leverage = Pipeline.objects.get(id=pipeline_id).leverage

            new_trade = Trade.objects.create(
                symbol_id=symbol,
                open_price=new_order.price,
                amount=new_order.executed_qty,
                side=1 if new_order.side == "BUY" else -1,
                exchange_id=self.exchange,
                mock=new_order.mock,
                pipeline_id=pipeline_id,
                leverage=leverage
            )

            return new_trade

        return None

    def print_trading_results(self, header, date, **kwargs):

        initial_balance = self._get_balances(kwargs.get("symbol", ""))[0]
        current_balance = self._get_balances(kwargs.get("symbol", ""))[1]

        try:
            perf = (current_balance - initial_balance) / initial_balance * 100
        except ZeroDivisionError:
            perf = 0

        self.print_current_balance(date, header=header, **kwargs)

        header = header

        logging.info(header + f"" + 100 * "-")
        logging.info(header + f"{date} | +++ CLOSED FINAL POSITION +++")
        logging.info(header + f"{date} | net performance (%) = {round(perf, 2)}")
        logging.info(header + f"{date} | number of trades executed = {self.nr_trades}")
        logging.info(header + f"" + 100 * "-")

    @staticmethod
    def _get_average_order_price(order):
        s = sum([float(fill["price"]) * float(fill["qty"]) for fill in order["fills"]])
        return s / float(order["executedQty"])

    def report_trade(self, order, units, going, header='', **kwargs):
        logging.debug(order)

        price = order["price"]

        date = order["transact_time"]

        logging.info(header + f"" + 100 * "-")
        logging.info(header + f"{date} | {going}")
        logging.info(header + f"units = {units} | price = {price}")

        self.print_current_nav(date, price, header, **kwargs)
        self.print_current_balance(date, header, **kwargs)
        self.print_current_position_value(date, price, header, **kwargs)

        logging.info(header + f"" + 100 * "-")
