import os
import sys

import django

module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Asset, Symbol, Exchange
from shared.exchanges import BinanceHandler


def main():
    bh = BinanceHandler(paper_trading=True)

    info = bh.futures_exchange_info()

    for symbol in info['symbols']:
        if symbol["quoteAsset"] == 'USDT' and symbol["contractType"] == 'PERPETUAL':
            quote_asset, _ = Asset.objects.get_or_create(symbol=symbol["quoteAsset"])
            base_asset, _ = Asset.objects.get_or_create(symbol=symbol["baseAsset"])

            try:
                Symbol.objects.get_or_create(
                    name=symbol["symbol"],
                    base=base_asset,
                    quote=quote_asset,
                    price_precision=symbol["pricePrecision"],
                    quantity_precision=symbol["quantityPrecision"]
                )
            except django.db.utils.IntegrityError:
                Symbol.objects.filter(name=symbol["symbol"]).update(
                    base=base_asset,
                    quote=quote_asset,
                    price_precision=symbol["pricePrecision"],
                    quantity_precision=symbol["quantityPrecision"]
                )

    Exchange.objects.get_or_create(name='binance')


if __name__ == "__main__":
    main()