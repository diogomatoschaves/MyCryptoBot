import os
from os import environ as env

import django
from dotenv import load_dotenv, find_dotenv
from binance.client import Client

import shared.exchanges.binance.constants as const
from shared.utils.decorators.failed_connection import retry_failed_connection
from shared.utils.exceptions import SymbolInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Symbol


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


class BinanceHandler(Client):

    @retry_failed_connection(num_times=3)
    def __init__(self, paper_trading=False, base_candle_size='5m'):

        self.paper_trading = paper_trading

        self.base_candle_size = base_candle_size

        self._get_api_keys(paper_trading=paper_trading)

        if not os.getenv('TEST'):
            Client.__init__(
                self,
                self.binance_api_key,
                self.binance_api_secret,
                testnet=paper_trading
            )
        else:
            self.session = None

    def _get_api_keys(self, paper_trading):

        if paper_trading:
            self.binance_api_key = env.get(const.BINANCE_API_KEY_TEST)
            self.binance_api_secret = env.get(const.BINANCE_API_SECRET_TEST)
        else:
            self.binance_api_key = env.get(const.BINANCE_API_KEY)
            self.binance_api_secret = env.get(const.BINANCE_API_SECRET)

    @staticmethod
    def validate_symbol(symbol):
        if not Symbol.objects.filter(name=symbol).exists():
            raise SymbolInvalid(symbol)
        else:
            return Symbol.objects.get(name=symbol)
