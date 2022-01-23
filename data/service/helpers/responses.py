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


ReturnCodes = RESPONSES(
    DATA_PIPELINE_START_OK="DATA_PIPELINE_START_OK",
    DATA_PIPELINE_ONGOING="DATA_PIPELINE_ONGOING",
    DATA_PIPELINE_STOPPED="DATA_PIPELINE_STOPPED",
    DATA_PIPELINE_INEXISTENT="DATA_PIPELINE_INEXISTENT",
    SYMBOL_REQUIRED="SYMBOL_REQUIRED",
    SYMBOL_INVALID="SYMBOL_INVALID",
    EXCHANGE_REQUIRED="EXCHANGE_REQUIRED",
    EXCHANGE_INVALID="EXCHANGE_INVALID",
    CANDLE_SIZE_REQUIRED="CANDLE_SIZE_REQUIRED",
    CANDLE_SIZE_INVALID="CANDLE_SIZE_INVALID",
    STRATEGY_REQUIRED="STRATEGY_REQUIRED",
    STRATEGY_INVALID="STRATEGY_INVALID",
    PARAMS_INVALID="PARAMS_INVALID",
    PARAMS_REQUIRED="PARAMS_REQUIRED"
)


Responses = RESPONSES(
    DATA_PIPELINE_START_OK=lambda pipeline: {"code": ReturnCodes.DATA_PIPELINE_START_OK,
                                             "message": f"Trading Bot successfully started.",
                                             "success": True, "pipeline": pipeline.as_json()},
    DATA_PIPELINE_ONGOING=lambda pipeline_id: {"code": ReturnCodes.DATA_PIPELINE_ONGOING,
                                               "message": f"Trading Bot already ongoing.", "success": False,
                                               "pipelineId": pipeline_id},
    DATA_PIPELINE_STOPPED=lambda pipeline: {"code": ReturnCodes.DATA_PIPELINE_STOPPED,
                                            "message": f"Trading Bot stopped.",
                                            "success": True, "pipeline": pipeline.as_json()},
    DATA_PIPELINE_INEXISTENT={"code": ReturnCodes.DATA_PIPELINE_INEXISTENT,
                              "message": f"This Trading Bot is not active.", "success": False},
    SYMBOL_REQUIRED={"code": ReturnCodes.SYMBOL_REQUIRED,
                     "message": "A symbol must be included in the request.", "success": False},
    SYMBOL_INVALID=lambda symbol: {"code": ReturnCodes.SYMBOL_INVALID,
                                   "message": f"{symbol} is not a valid symbol.", "success": False},
    EXCHANGE_REQUIRED={"code": ReturnCodes.EXCHANGE_REQUIRED,
                       "message": "An exchange must be included in the request.", "success": False},
    EXCHANGE_INVALID=lambda exchange: {"code": ReturnCodes.EXCHANGE_INVALID,
                                       "message": f"{exchange} is not a valid exchange.", "success": False},
    CANDLE_SIZE_REQUIRED={"code": ReturnCodes.CANDLE_SIZE_REQUIRED,
                          "message": "A candle size must be included in the request.", "success": False},
    CANDLE_SIZE_INVALID=lambda candle_size: {"code": ReturnCodes.CANDLE_SIZE_INVALID,
                                             "message": f"{candle_size} is not a valid candle size.", "success": False},
    STRATEGY_REQUIRED={"code": ReturnCodes.STRATEGY_REQUIRED,
                       "message": "A strategy must be included in the request.", "success": False},
    STRATEGY_INVALID=lambda strategy: {"code": ReturnCodes.STRATEGY_INVALID,
                                       "message": f"{strategy} is not a valid strategy.", "success": False},
    PARAMS_INVALID=lambda param_key: {"code": ReturnCodes.PARAMS_INVALID,
                                      "message": f"Provided {param_key} in params is not valid.", "success": False},
    PARAMS_REQUIRED=lambda param_key: {"code": ReturnCodes.PARAMS_REQUIRED,
                                       "message": f"{param_key} is a required parameter.", "success": False},
)
