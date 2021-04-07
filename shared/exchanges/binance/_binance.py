from os import environ as env

from dotenv import load_dotenv, find_dotenv
from binance.client import Client

import shared.exchanges.binance.constants as const

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


class BinanceHandler(Client):

    def __init__(self):
        # self.API_KEY = 'https://testnet.binance.vision/api'

        self._get_api_keys()

        Client.__init__(self, self.binance_api_key, self.binance_api_secret)

    def _get_api_keys(self):
        self.binance_api_key = env.get(const.BINANCE_API_KEY)
        self.binance_api_secret = env.get(const.BINANCE_API_SECRET)
