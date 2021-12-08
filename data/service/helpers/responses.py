from collections import namedtuple


RESPONSES = namedtuple(
    'Responses',
    [
        "DATA_PIPELINE_START_OK",
        "DATA_PIPELINE_ONGOING",
        "DATA_PIPELINE_STOPPED",
        "DATA_PIPELINE_INEXISTENT",
        "SYMBOL_REQUIRED",
        "SYMBOL_INVALID",
        "EXCHANGE_REQUIRED",
        "EXCHANGE_INVALID",
        "CANDLE_SIZE_REQUIRED",
        "CANDLE_SIZE_INVALID",
        "STRATEGY_REQUIRED",
        "STRATEGY_INVALID",
        "PARAMS_INVALID",
        "PARAMS_REQUIRED"
    ]
)


Responses = RESPONSES(
    DATA_PIPELINE_START_OK=lambda pipeline_id: {"response": f"Data pipeline successfully started.",
                                                "success": True, "pipeline_id": pipeline_id},
    DATA_PIPELINE_ONGOING={"response": f"Data pipeline already ongoing.", "success": False},
    DATA_PIPELINE_STOPPED={"response": f"Data pipeline stopped.", "success": True},
    DATA_PIPELINE_INEXISTENT={"response": f"This data pipeline is not active.", "success": False},
    SYMBOL_REQUIRED={"response": "A symbol must be included in the request.", "success": False},
    SYMBOL_INVALID=lambda symbol: {"response": f"{symbol} is not a valid symbol.", "success": False},
    EXCHANGE_REQUIRED={"response": "An exchange must be included in the request.", "success": False},
    EXCHANGE_INVALID=lambda exchange: {"response": f"{exchange} is not a valid exchange.", "success": False},
    CANDLE_SIZE_REQUIRED={"response": "A candle size must be included in the request.", "success": False},
    CANDLE_SIZE_INVALID=lambda candle_size: {"response": f"{candle_size} is not a valid candle size.", "success": False},
    STRATEGY_REQUIRED={"response": "A strategy must be included in the request.", "success": False},
    STRATEGY_INVALID=lambda strategy: {"response": f"{strategy} is not a valid strategy.", "success": False},
    PARAMS_INVALID=lambda param_key: {"response": f"Provided {param_key} in params is not valid.", "success": False},
    PARAMS_REQUIRED=lambda param_key: {"response": f"{param_key} is a required parameter.", "success": False},
)
