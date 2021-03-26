import logging
import os
import re
from os import environ as env
from datetime import datetime, timedelta

import pytz
from dotenv import load_dotenv, find_dotenv
from binance.client import Client
from binance.websockets import BinanceSocketManager
from django.db import connection
import pandas as pd
import django
import numpy as np

from data_processing.extract.scrapers.binance.binance import get_historical_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import ExchangeData
from trading_automation.trading import Trader
import trading_automation.binance.constants as const


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


class BinanceTrader(Client, BinanceSocketManager, Trader):

    AUTO_REPAY = 'AUTO_REPAY'

    def __init__(
        self,
        strategy,
        quote='USDT',
        base='BTC',
        candle_size='5m',
        margin_level=3,
        price_col='close',
        returns_col='returns'
    ):
        # self.API_KEY = 'https://testnet.binance.vision/api'

        self._get_api_keys()

        Client.__init__(self, self.binance_api_key, self.binance_api_secret)
        BinanceSocketManager.__init__(self, self)

        self.strategy = strategy
        self.returns_col = returns_col
        self.price_col = price_col

        self.quote = quote
        self.base = base
        self.symbol = base + quote
        self.exchange = 'binance'
        self.candle_size = candle_size

        self.asset_info = {asset["symbol"]: asset for asset in self.get_isolated_margin_account()["assets"]}
        self.margin_level = margin_level
        self.max_margin_level = int(self.asset_info[self.symbol]["marginRatio"])
        if self.margin_level > self.max_margin_level:
            self.margin_level = self.max_margin_level

        Trader.__init__(self, self._get_symbol_account_total(self.asset_info[self.symbol]))

        self._open_orders = []
        self.filled_orders = []
        self.conn_key = None

        self.trading_fees = self.get_trade_fee(symbol=self.symbol)['tradeFee'][0]

    def start_trading(self):

        self._get_gistorical_data()

        self._get_data()
        self._start_websocket(self.symbol, self.websocket_callback)

    def stop_trading(self):
        self.stop_socket(self.conn_key)

        self.close_pos(date=datetime.utcnow(), row=None)

    def _get_api_keys(self):
        self.binance_api_key = env.get(const.BINANCE_API_KEY)
        self.binance_api_secret = env.get(const.BINANCE_API_SECRET)

    @staticmethod
    def _get_symbol_account_total(asset_info):
        amount = float(asset_info["quoteAsset"]["netAsset"])
        amount += float(asset_info["baseAsset"]["netAsset"]) * float(asset_info["indexPrice"])

        return amount

    def _get_loan_amount(self):
        details = self.get_max_margin_loan(asset=self.quote, isolatedSymbol=self.symbol)

        return np.ceil(float(details["amount"])) * (self.margin_level / self.max_margin_level)

    def _get_gistorical_data(self):

        print(f"Getting historical data up until now ({datetime.utcnow()})...")

        start_date = ExchangeData.objects\
            .filter(exchange=self.exchange, symbol=self.symbol)\
            .order_by('open_time').last().open_time - timedelta(hours=5)

        get_historical_data(
            'binance',
            self,
            self.base,
            self.quote,
            self.KLINE_INTERVAL_1MINUTE,
            int(start_date.timestamp() * 1000)
        )

    def _get_query(self, days):

        query = str(
            ExchangeData.objects.filter(
                exchange=f"'{self.exchange}'",
                symbol=f"'{self.symbol}'",
                open_time__gte=f"{(datetime.utcnow() - timedelta(days=days)).date()}"
            ).order_by('open_time').query
        )

        pattern = r"\d{4}-\d{2}-\d{2}\s*\d+:\d+:\d+"
        query = re.sub(pattern, r'"\g<0>"', query)

        return query

    def _get_data(self):

        print(f"Loading the data...")

        query = self._get_query(20)

        # TODO: Adjust time based on candle size
        self.data = pd.read_sql_query(query, connection, parse_dates=['open_time'], index_col='open_time')

        self.data = self._resample_data(self.data, const.COLUMNS_AGGREGATION).iloc[:-1]
        self.data_length = len(self.data)

    def _resample_data(self, data, aggregation_method):
        return data \
            .resample(const.CANDLE_SIZES_MAPPER[self.candle_size]) \
            .agg(aggregation_method) \
            .ffill()

    def _prepare_data(self):
        data = self.data.copy()
        data[self.returns_col] = np.log(data[self.price_col] / data[self.price_col].shift(1))
        data = self.strategy.update_data(data)

        return data

    def websocket_callback(self, row):

        # self.stop_trading()
        # print(row)

        df = pd.DataFrame(
            {
                const.NAME_MAPPER[key]: [const.FUNCTION_MAPPER[key](value)]
                for key, value in row["k"].items()
                if key in const.NAME_MAPPER
            }
        ).set_index('open_time')

        self.data = self.data.append(df)

        self.data = self._resample_data(self.data, const.COLUMNS_AGGREGATION_WEBSOCKET)

        # TODO: Save last_row in database
        if len(self.data) != self.data_length:

            self.data_length = len(self.data)

            data = self._prepare_data()[:-1]

            last_row = data.iloc[-1]

            signal = self.strategy.get_signal(last_row)

            if signal == self.position:
                print(f"{last_row.name} | Last close price: {last_row[self.price_col]}")

            amount = 'all'
            if self.position == 0:
                amount = self._get_loan_amount()

            self.trade(signal, last_row.name, last_row, amount=amount)

    def buy_instrument(self, date, row, units=None, amount=None, **kwargs):
        self._execute_order(
            self.ORDER_TYPE_MARKET,
            self.SIDE_BUY,
            "GOING LONG",
            units=units,
            amount=amount,
            **kwargs
        )

    def sell_instrument(self, date, row, units=None, amount=None, **kwargs):
        self._execute_order(
            self.ORDER_TYPE_MARKET,
            self.SIDE_SELL,
            "GOING SHORT",
            units=units,
            amount=amount,
            **kwargs
        )

    def close_pos(self, date, row):

        if self.units <= 0:
            self.buy_instrument(date, row, units=-self.units, side_effect=self.AUTO_REPAY)
        else:
            self.sell_instrument(date, row, units=self.units, side_effect=self.AUTO_REPAY)

        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        self.print_current_balance(date)

        print(100 * "-")
        print("{} | +++ CLOSED FINAL POSITION +++".format(date))
        print("{} | net performance (%) = {}".format(date, round(perf, 2)))
        print("{} | number of trades executed = {}".format(date, self.trades))
        print(100 * "-")

    def _execute_order(self, order_type, order_side, going, side_effect='MARGIN_BUY', units=None, amount=None):

        kwargs = self._get_order_kwargs(units, amount)

        order = self.create_margin_order(
            symbol=self.symbol,
            side=order_side,
            type=order_type,
            newOrderRespType='FULL',
            isIsolated=True,
            sideEffectType=side_effect,
            **kwargs
        )

        self.filled_orders.append(order)

        units = float(order["executedQty"])
        price = self._get_average_order_price(order)

        factor = 1 if order_side == self.SIDE_SELL else -1

        self.current_balance += factor * float(order['cummulativeQuoteQty'])
        self.units -= factor * units
        self.trades += 1

        self.report_trade(order, units, price, going)

    @staticmethod
    def _get_order_kwargs(units, amount):
        kwargs = {}
        if units:
            kwargs["quantity"] = units
        elif amount:
            kwargs["quoteOrderQty"] = amount

        return kwargs

    @staticmethod
    def _get_average_order_price(order):

        s = sum([float(fill["price"]) * float(fill["qty"]) for fill in order["fills"]])

        return s / float(order["executedQty"])

    def _start_websocket(self, symbol, callback, option='kline'):
        print(f"Starting data stream...")

        self.conn_key = getattr(self, f'start_{option}_socket')(symbol=symbol, callback=callback, interval=self.candle_size)
        self.start()

    def report_trade(self, order, units, price, going):

        date = datetime.fromtimestamp(order["transactTime"] / 1000).astimezone(pytz.utc)

        print(100 * "-")
        print("{} | {}".format(date, going))
        print("{} | units = {} | price = {}".format(date, units, price))
        self.print_current_nav(date, price)
        print(100 * "-")
