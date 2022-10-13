from random import randint

isolated_account_info = {
    "assets": [
        {
            "baseAsset": {
                "asset": "BTC",
                "borrowEnabled": True,
                "borrowed": "10.00000000",
                "free": "10.00000000",
                "interest": "0.00000000",
                "locked": "0.00000000",
                "netAsset": "0.00000000",
                "netAssetOfBtc": "0.00000000",
                "repayEnabled": True,
                "totalAsset": "0.00000000",
            },
            "quoteAsset": {
                "asset": "USDT",
                "borrowEnabled": True,
                "borrowed": "10.00000000",
                "free": "100.00000000",
                "interest": "0.00000000",
                "locked": "0.00000000",
                "netAsset": "90.00000000",
                "netAssetOfBtc": "0.00000000",
                "repayEnabled": True,
                "totalAsset": "0.00000000",
            },
            "symbol": "BTCUSDT",
            "isolatedCreated": True,
            "marginLevel": "10.00000000",
            "marginLevelStatus": "EXCESSIVE",
            "marginRatio": "10.00000000",
            "indexPrice": "10000.00000000",
            "liquidatePrice": "1000.00000000",
            "liquidateRate": "1.00000000",
            "tradeEnabled": True,
        }
    ],
    "totalAssetOfBtc": "0.00000000",
    "totalLiabilityOfBtc": "0.00000000",
    "totalNetAssetOfBtc": "0.00000000",
}

trading_fees = {
    "tradeFee": [
        {"symbol": "BTCUSDT", "maker": 0.9000, "taker": 1.0000},
    ],
    "success": True,
}


margin_order_creation = {
    "symbol": "BTCUSDT",
    "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
    "transactTime": 1507725176595,
    "price": "3998.3",
    "origQty": "10.00000000",
    "executedQty": "10.00000000",
    "cummulativeQuoteQty": "10.00000000",
    "status": "FILLED",
    "timeInForce": "GTC",
    "type": "MARKET",
    "side": "SELL",
    "marginBuyBorrowAmount": 5,  # will not return if no margin trade happens
    "marginBuyBorrowAsset": "BTC",  # will not return if no margin trade happens
    "isIsolated": True,  # if isolated margin
    "fills": [
        {
            "price": "4000.00000000",
            "qty": "1.00000000",
            "commission": "4.00000000",
            "commissionAsset": "USDT",
        },
        {
            "price": "3999.00000000",
            "qty": "5.00000000",
            "commission": "19.99500000",
            "commissionAsset": "USDT",
        },
        {
            "price": "3998.00000000",
            "qty": "2.00000000",
            "commission": "7.99600000",
            "commissionAsset": "USDT",
        },
        {
            "price": "3997.00000000",
            "qty": "1.00000000",
            "commission": "3.99700000",
            "commissionAsset": "USDT",
        },
        {
            "price": "3995.00000000",
            "qty": "1.00000000",
            "commission": "3.99500000",
            "commissionAsset": "USDT",
        },
    ],
}

futures_order_creation = {
    "orderId": 3214109855,
    "symbol": "BTCUSDT",
    "status": "FILLED",
    "clientOrderId": "6MyYUkDJ4wU16daDkGXzy5",
    "price": "19298.33000",
    "avgPrice": "19298.33000",
    "origQty": "0.040",
    "executedQty": "0.040",
    "cumQty": "0.040",
    "cumQuote": "771.93320",
    "timeInForce": "GTC",
    "type": "MARKET",
    "reduceOnly": True,
    "closePosition": False,
    "side": "SELL",
    "positionSide": "BOTH",
    "stopPrice": "0",
    "workingType": "CONTRACT_PRICE",
    "priceProtect": False,
    "origType": "MARKET",
    "updateTime": 1663601948038
}

exchange_info = {
    "symbols": [
        {
            'symbol': 'BTCUSDT',
            'pair': 'BTCUSDT',
            'contractType': 'PERPETUAL',
            'deliveryDate': 4133404800000,
            'onboardDate': 1569398400000,
            'status': 'TRADING',
            'maintMarginPercent': '2.5000',
            'requiredMarginPercent': '5.0000',
            'baseAsset': 'BTC',
            'quoteAsset': 'USDT',
            'marginAsset': 'USDT',
            'pricePrecision': 2,
            'quantityPrecision': 3,
            'baseAssetPrecision': 8,
            'quotePrecision': 8,
            'underlyingType': 'COIN',
            'underlyingSubType': ['PoW'],
            'settlePlan': 0,
            'triggerProtect': '0.0500',
            'liquidationFee': '0.017500',
            'marketTakeBound': '0.05',
            'filters': [{'minPrice': '556.80',
                         'maxPrice': '4529764',
                         'filterType': 'PRICE_FILTER',
                         'tickSize': '0.10'},
                        {'stepSize': '0.001',
                         'filterType': 'LOT_SIZE',
                         'maxQty': '1000',
                         'minQty': '0.001'},
                        {'stepSize': '0.001',
                         'filterType': 'MARKET_LOT_SIZE',
                         'maxQty': '120',
                         'minQty': '0.001'},
                        {'limit': 200, 'filterType': 'MAX_NUM_ORDERS'},
                        {'limit': 10, 'filterType': 'MAX_NUM_ALGO_ORDERS'},
                        {'notional': '5', 'filterType': 'MIN_NOTIONAL'},
                        {'multiplierDown': '0.9500',
                         'multiplierUp': '1.0500',
                         'multiplierDecimal': '4',
                         'filterType': 'PERCENT_PRICE'}],
            'orderTypes': ['LIMIT',
                           'MARKET',
                           'STOP',
                           'STOP_MARKET',
                           'TAKE_PROFIT',
                           'TAKE_PROFIT_MARKET',
                           'TRAILING_STOP_MARKET'],
            'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX']
        }
    ]
}
