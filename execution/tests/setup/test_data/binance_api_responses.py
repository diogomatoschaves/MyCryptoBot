isolated_account_info = {
    "assets": [
        {
            "baseAsset": {
                "asset": "BTC",
                "borrowEnabled": True,
                "borrowed": "0.00000000",
                "free": "0.00000000",
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


order_creation = {
    "symbol": "BTCUSDT",
    "orderId": 28,
    "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
    "transactTime": 1507725176595,
    "price": "1.00000000",
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
