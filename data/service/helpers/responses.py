

RESPONSES = {
    "DATA_PIPELINE_START_OK": lambda symbol: {"response": f"{symbol} data pipeline successfully started."},
    "DATA_PIPELINE_ONGOING": lambda symbol: {"response": f"{symbol} data pipeline already ongoing."},
    "SYMBOL_REQUIRED": {"response": "A symbol must be included in the request."},
    "SYMBOL_INVALID": lambda symbol: {"response": f"{symbol} is not a valid symbol."},
    "EXCHANGE_REQUIRED": {"response": "An exchange must be included in the request."},
    "EXCHANGE_INVALID": lambda exchange: {"response": f"{exchange} is not a valid exchange."},
    "CANDLE_SIZE_REQUIRED": {"response": "A candle size must be included in the request."},
    "CANDLE_SIZE_INVALID": lambda candle_size: {"response": f"{candle_size} is not a valid candle size."},
    "STRATEGY_REQUIRED": {"response": "A strategy must be included in the request."},
    "STRATEGY_INVALID": lambda strategy: {"response": f"{strategy} is not a valid strategy."},
    "PARAMS_INVALID": lambda param_key: {"response": f"Provided {param_key} in params is not valid."},
}
