import logging
import os
from datetime import datetime

import django
import numpy as np
import pandas as pd
import pytz
from stratestic.trading import Trader
from stratestic.backtesting.helpers.evaluation import (
    get_overview_results,
    get_returns_results,
    get_drawdown_results,
    get_trades_results,
    log_results
)
from stratestic.backtesting.helpers.evaluation.metrics import exposure_time

from shared.exchanges.binance import BinanceHandler
from shared.utils.helpers import get_pipeline_data, convert_trade

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

        self.position = {}
        self.filled_orders = []
        self.exchange = "binance"
        self.start_date = {}

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

        super()._set_position(symbol, position)

        pipeline_id = kwargs.pop("pipeline_id", None)

        previous_position = kwargs.pop("previous_position", 0)

        new_trade = self._handle_trades(pipeline_id, symbol, previous_position, position)

        if Position.objects.filter(pipeline_id=pipeline_id).exists():
            if position == 0:
                Position.objects.filter(
                    pipeline_id=pipeline_id,
                ).update(
                    position=position,
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
                        open_time=datetime.now(tz=pytz.UTC),
                        buying_price=new_trade.open_price,
                        amount=new_trade.amount
                    )
        else:
            Position.objects.create(
                position=position,
                pipeline_id=pipeline_id,
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

        Orders.objects.create(**formatted_order)

        return formatted_order

    def _get_position(self, symbol):
        return self.position[symbol]

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

            closing_order = orders.pop()

            last_trade = Trade.objects.filter(pipeline_id=pipeline_id, symbol_id=symbol).last()

            if last_trade:
                last_trade.close_price = closing_order.price
                last_trade.close_time = datetime.now(tz=pytz.UTC)
                last_trade.pnl = last_trade.get_profit_loss()
                last_trade.pnl_pct = last_trade.get_profit_loss_pct()
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
    
    @staticmethod
    def _process_trading_bot_results(trades):
        df = pd.DataFrame(trades)

        df = pd.concat([df.iloc[0:1, :], df], axis=0, ignore_index=True)

        df.loc[0, 'pnl'] = 0
        df.loc[0, 'side'] = 0

        df = df.rename(columns={'pnl': "strategy_returns_tc", "exit_date": "close_date"}).set_index('entry_date')

        df["accumulated_strategy_returns_tc"] = df["strategy_returns_tc"].cumsum().apply(np.exp)

        return df

    def print_trading_results(self, pipeline_id):
        pipeline = get_pipeline_data(pipeline_id)

        # Retrieve trading bot data
        trades = Trade.objects.filter(
            pipeline__id=pipeline_id,
            open_time__gte=self.start_date[pipeline.symbol],
            close_time__isnull=False
        ).order_by('open_time')

        if len(trades) == 0:
            logging.debug('There are no executed trades.')
            return

        trades = [convert_trade(trade) for trade in trades]

        data = self._process_trading_bot_results(trades)

        leverage = pipeline.leverage
        amount = self.initial_balance[pipeline.symbol]
        results = {}

        # Get metrics
        results = get_overview_results(results, data, leverage, None, amount * pipeline.leverage)

        results = get_returns_results(results, data, amount, trading_days=365)

        results = get_drawdown_results(results, data)

        results = get_trades_results(results, trades)

        results["exposure_time"] = exposure_time(self.positions)
        results["start_date"] = results["start_date"].round('min')
        results["end_date"] = results["end_date"].round('min')
        results["max_trade_duration"] = pd.Timedelta(results["max_trade_duration"]).round('1s')
        results["avg_trade_duration"] = pd.Timedelta(seconds=results["avg_trade_duration"]).round('1s')

        # print results
        log_results(results, backtesting=False)

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
