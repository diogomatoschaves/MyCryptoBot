from collections import namedtuple


RESPONSES = namedtuple(
    'Responses',
    [
        "DATA_PIPELINE_START_OK",
        "DATA_PIPELINE_ONGOING",
        "DATA_PIPELINE_STOPPED",
        "DATA_PIPELINE_DOES_NOT_EXIST",
        "SYMBOL_REQUIRED",
        "SYMBOL_INVALID",
        "EXCHANGE_REQUIRED",
        "EXCHANGE_INVALID",
        "CANDLE_SIZE_REQUIRED",
        "CANDLE_SIZE_INVALID",
        "STRATEGY_REQUIRED",
        "STRATEGY_INVALID",
        "PARAMS_INVALID",
        "PARAMS_REQUIRED",
        "NAME_INVALID",
        "NAME_REQUIRED",
        "COLOR_REQUIRED",
        "LEVERAGE_INVALID"
    ]
)


ReturnCodes = RESPONSES(
    DATA_PIPELINE_START_OK="DATA_PIPELINE_START_OK",
    DATA_PIPELINE_ONGOING="DATA_PIPELINE_ONGOING",
    DATA_PIPELINE_STOPPED="DATA_PIPELINE_STOPPED",
    DATA_PIPELINE_DOES_NOT_EXIST="DATA_PIPELINE_DOES_NOT_EXIST",
    SYMBOL_REQUIRED="SYMBOL_REQUIRED",
    SYMBOL_INVALID="SYMBOL_INVALID",
    EXCHANGE_REQUIRED="EXCHANGE_REQUIRED",
    EXCHANGE_INVALID="EXCHANGE_INVALID",
    CANDLE_SIZE_REQUIRED="CANDLE_SIZE_REQUIRED",
    CANDLE_SIZE_INVALID="CANDLE_SIZE_INVALID",
    STRATEGY_REQUIRED="STRATEGY_REQUIRED",
    STRATEGY_INVALID="STRATEGY_INVALID",
    PARAMS_INVALID="PARAMS_INVALID",
    PARAMS_REQUIRED="PARAMS_REQUIRED",
    NAME_INVALID="NAME_INVALID",
    NAME_REQUIRED="NAME_REQUIRED",
    COLOR_REQUIRED="COLOR_REQUIRED",
    LEVERAGE_INVALID="LEVERAGE_INVALID"
)


Responses = RESPONSES(
    DATA_PIPELINE_START_OK=lambda pipeline: {"code": ReturnCodes.DATA_PIPELINE_START_OK,
                                             "message": f"Trading Bot successfully started.",
                                             "success": True, "pipeline": pipeline.as_json()},
    DATA_PIPELINE_ONGOING=lambda message, pipeline_id: {"code": ReturnCodes.DATA_PIPELINE_ONGOING,
                                                        "message": message, "success": False,
                                                        "pipelineId": pipeline_id},
    DATA_PIPELINE_STOPPED=lambda pipeline: {"code": ReturnCodes.DATA_PIPELINE_STOPPED,
                                            "message": f"Trading Bot stopped.",
                                            "success": True, "pipeline": pipeline.as_json()},
    DATA_PIPELINE_DOES_NOT_EXIST=lambda message: {"code": ReturnCodes.DATA_PIPELINE_DOES_NOT_EXIST,
                                                  "message": message, "success": False},
    SYMBOL_REQUIRED=lambda message: {"code": ReturnCodes.SYMBOL_REQUIRED,
                                     "message": message, "success": False},
    SYMBOL_INVALID=lambda message: {"code": ReturnCodes.SYMBOL_INVALID,
                                    "message": message, "success": False},
    EXCHANGE_REQUIRED=lambda message: {"code": ReturnCodes.EXCHANGE_REQUIRED,
                                       "message": message, "success": False},
    EXCHANGE_INVALID=lambda message: {"code": ReturnCodes.EXCHANGE_INVALID,
                                      "message": message, "success": False},
    CANDLE_SIZE_REQUIRED=lambda message: {"code": ReturnCodes.CANDLE_SIZE_REQUIRED,
                                          "message": message, "success": False},
    CANDLE_SIZE_INVALID=lambda message: {"code": ReturnCodes.CANDLE_SIZE_INVALID,
                                         "message": message, "success": False},
    STRATEGY_REQUIRED=lambda message: {"code": ReturnCodes.STRATEGY_REQUIRED,
                                       "message": message, "success": False},
    STRATEGY_INVALID=lambda message: {"code": ReturnCodes.STRATEGY_INVALID,
                                      "message": message, "success": False},
    PARAMS_INVALID=lambda message: {"code": ReturnCodes.PARAMS_INVALID,
                                    "message": message, "success": False},
    PARAMS_REQUIRED=lambda message: {"code": ReturnCodes.PARAMS_REQUIRED,
                                     "message": message, "success": False},
    NAME_INVALID=lambda message: {"code": ReturnCodes.NAME_INVALID,
                                  "message": message, "success": False},
    NAME_REQUIRED=lambda message: {"code": ReturnCodes.NAME_REQUIRED,
                                   "message": message, "success": False},
    COLOR_REQUIRED=lambda message: {"code": ReturnCodes.COLOR_REQUIRED,
                                    "message": message, "success": False},
    LEVERAGE_INVALID=lambda message: {"code": ReturnCodes.LEVERAGE_INVALID,
                                      "message": message, "success": False}
)
