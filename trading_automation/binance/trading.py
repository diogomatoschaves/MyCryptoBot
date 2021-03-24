import logging
import os
from os import environ as env
from datetime import datetime, timedelta

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

    def __init__(
        self,
        strategy,
        quote='USDT',
        base='BTC',
        candle_size='5m',
        margin_level=10,
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
        if self.margin_level > int(self.asset_info[self.symbol]["marginRatio"]):
            self.margin_level = int(self.asset_info[self.symbol]["marginRatio"])

        Trader.__init__(self, self._get_symbol_account_total(self.asset_info[self.symbol]))

        self._open_orders = []
        self._filled_orders = []
        self.conn_key = None

        self.trading_fees = self.get_trade_fee(symbol=self.symbol)['tradeFee'][0]

    def _get_api_keys(self):
        self.binance_api_key = env.get(const.BINANCE_API_KEY)
        self.binance_api_secret = env.get(const.BINANCE_API_SECRET)

    @staticmethod
    def _get_symbol_account_total(asset_info):
        amount = float(asset_info["quoteAsset"]["netAsset"])
        amount += float(asset_info["baseAsset"]["netAsset"]) * float(asset_info["indexPrice"])

        return amount

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

    def _get_data(self):

        print(f"Loading the data...")

        query = str(
            ExchangeData.objects.filter(
                exchange=f"'{self.exchange}'",
                symbol=f"'{self.symbol}'",
                # open_time__gte=f"'{(datetime.utcnow() - timedelta(days=365)).date()}'"
            ).query
        )

        min_date = (datetime.utcnow() - timedelta(days=5)).date()

        self.data = pd.read_sql_query(query, connection, parse_dates=['open_time'], index_col='open_time').loc[min_date:].copy()

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

    # TODO: Process incoming data and execute trades
    def websocket_callback(self, row):

        self.stop_trading()
        print(row)

        df = pd.DataFrame(
            {
                const.NAME_MAPPER[key]: [const.FUNCTION_MAPPER[key](value)]
                for key, value in row["k"].items()
                if key in const.NAME_MAPPER
            }
        ).set_index('open_time')

        self.data = self.data.append(df)

        self.data = self._resample_data(self.data, const.COLUMNS_AGGREGATION_WEBSOCKET)

        if len(self.data) != self.data_length:

            self.data_length = len(self.data)

            data = self._prepare_data()[:-1]

            a = 1

    def start_trading(self):

        self._get_gistorical_data()

        self._get_data()
        self._start_websocket(self.symbol, self.websocket_callback)

    def _start_websocket(self, symbol, callback, option='kline'):
        print(f"Starting websocket...")

        self.conn_key = getattr(self, f'start_{option}_socket')(symbol=symbol, callback=callback, interval=self.candle_size)
        self.start()

    def stop_trading(self):
        self.stop_socket(self.conn_key)

    def buy_instrument(self, date, row, units=None, amount=None):

        if units is None:
            units = amount / price

        self.current_balance -= units * price
        self.units += units
        self.trades += 1
        print(f"{date} |  Buying {round(units, 4)} {self.symbol} for {round(price, 5)}")

    def sell_instrument(self, date, row, units=None, amount=None):
        raise NotImplementedError

    def execute_trades(self):

        # executing trades
        if len(self.data) > self.data_length:
            self.data_length = len(self.data)
            if self.data["position"].iloc[-1] == 1:
                if self.position == 0:
                    order = self.create_order(self.symbol, self.units, suppress = True, ret = True)
                    self.report_trade(order, "GOING LONG")
                elif self.position == -1:
                    order = self.create_order(self.symbol, self.units * 2, suppress = True, ret = True)
                    self.report_trade(order, "GOING LONG")
                self.position = 1
            elif self.data["position"].iloc[-1] == -1:
                if self.position == 0:
                    order = self.create_order(self.symbol, -self.units, suppress = True, ret = True)
                    self.report_trade(order, "GOING SHORT")
                elif self.position == 1:
                    order = self.create_order(self.symbol, -self.units * 2, suppress = True, ret = True)
                    self.report_trade(order, "GOING SHORT")
                self.position = -1

    @staticmethod
    def report_trade(order, going):
        time = datetime.fromtimestamp(order["transactTime"])
        units = order["origQty"]
        price = order["price"]
        type_ = order["type"]
        side = order["side"]

        # pl = float(order["pl"])
        # self.profits.append(pl)
        # cumpl = sum(self.profits)
        print("\n" + 100* "-")
        print("{} | {}".format(time, going))
        print("{} | units = {} | price = {} | P&L = {} | Cum P&L = {}".format(time, units, price, pl, cumpl))
        print(100 * "-" + "\n")






    # def _get_client(self):
    #     self.client = Client(self.binance_api_key, self.binance_api_secret)._i
    #     return self.client

    # def start_client(self):
    #
    #     self._get_api_keys()
    #     client = self._get_client()
    #
    #     self._open_orders = client.get_all_margin_orders(symbol=self.symbol, limit=20, isIsolated=True)
    #
