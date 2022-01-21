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
    DATA_PIPELINE_START_OK=lambda pipeline_id: {"message": f"Data pipeline successfully started.",
                                                "success": True, "pipelineId": pipeline_id},
    DATA_PIPELINE_ONGOING=lambda pipeline_id: {"message": f"Data pipeline already ongoing.", "success": False,
                                               "pipelineId": pipeline_id},
    DATA_PIPELINE_STOPPED={"message": f"Data pipeline stopped.", "success": True},
    DATA_PIPELINE_INEXISTENT={"message": f"This data pipeline is not active.", "success": False},
    SYMBOL_REQUIRED={"message": "A symbol must be included in the request.", "success": False},
    SYMBOL_INVALID=lambda symbol: {"message": f"{symbol} is not a valid symbol.", "success": False},
    EXCHANGE_REQUIRED={"message": "An exchange must be included in the request.", "success": False},
    EXCHANGE_INVALID=lambda exchange: {"message": f"{exchange} is not a valid exchange.", "success": False},
    CANDLE_SIZE_REQUIRED={"message": "A candle size must be included in the request.", "success": False},
    CANDLE_SIZE_INVALID=lambda candle_size: {"message": f"{candle_size} is not a valid candle size.", "success": False},
    STRATEGY_REQUIRED={"message": "A strategy must be included in the request.", "success": False},
    STRATEGY_INVALID=lambda strategy: {"message": f"{strategy} is not a valid strategy.", "success": False},
    PARAMS_INVALID=lambda param_key: {"message": f"Provided {param_key} in params is not valid.", "success": False},
    PARAMS_REQUIRED=lambda param_key: {"message": f"{param_key} is a required parameter.", "success": False},
)
