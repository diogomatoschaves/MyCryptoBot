from collections import namedtuple


RESPONSES = namedtuple(
    'Responses',
    [
        "TRADING_SYMBOL_START",
        "TRADING_SYMBOL_STOP",
        "PIPELINE_NOT_ACTIVE",
        "NO_SUCH_PIPELINE",
        "SYMBOL_REQUIRED",
        "SYMBOL_INVALID",
        "EXCHANGE_REQUIRED",
        "EXCHANGE_INVALID",
        "SIGNAL_REQUIRED",
        "SIGNAL_INVALID",
        "ORDER_EXECUTION_SUCCESS",
        "EQUITY_REQUIRED",
        "API_ERROR",
        "SYMBOL_ALREADY_TRADED",
        "SYMBOL_NOT_BEING_TRADED",
        "LEVERAGE_SETTING_FAILURE",
        "NEGATIVE_EQUITY"
    ]
)


ReturnCodes = RESPONSES(
    TRADING_SYMBOL_START="TRADING_SYMBOL_START",
    TRADING_SYMBOL_STOP="TRADING_SYMBOL_STOP",
    PIPELINE_NOT_ACTIVE="PIPELINE_NOT_ACTIVE",
    NO_SUCH_PIPELINE="NO_SUCH_PIPELINE",
    SYMBOL_REQUIRED="SYMBOL_REQUIRED",
    SYMBOL_INVALID="SYMBOL_INVALID",
    EXCHANGE_REQUIRED="EXCHANGE_REQUIRED",
    EXCHANGE_INVALID="EXCHANGE_INVALID",
    SIGNAL_REQUIRED="SIGNAL_REQUIRED",
    SIGNAL_INVALID="SIGNAL_INVALID",
    ORDER_EXECUTION_SUCCESS="ORDER_EXECUTION_SUCCESS",
    EQUITY_REQUIRED="EQUITY_REQUIRED",
    API_ERROR="API_ERROR",
    SYMBOL_ALREADY_TRADED="SYMBOL_ALREADY_TRADED",
    SYMBOL_NOT_BEING_TRADED="SYMBOL_NOT_BEING_TRADED",
    LEVERAGE_SETTING_FAILURE="LEVERAGE_SETTING_FAILURE",
    NEGATIVE_EQUITY="NEGATIVE_EQUITY"
)


Responses = RESPONSES(
    TRADING_SYMBOL_START=lambda symbol: {
        "code": ReturnCodes.TRADING_SYMBOL_START,
        "success": True,
        "message": f"{symbol}: Trading symbol successfully started."
    },
    TRADING_SYMBOL_STOP=lambda symbol: {
        "code": ReturnCodes.TRADING_SYMBOL_STOP,
        "success": True,
        "message": f"{symbol}: Trading symbol successfully stopped."
    },
    PIPELINE_NOT_ACTIVE=lambda message: {
        "code": ReturnCodes.PIPELINE_NOT_ACTIVE,
        "success": False,
        "message":  message
    },
    NO_SUCH_PIPELINE=lambda message: {
        "code": ReturnCodes.NO_SUCH_PIPELINE,
        "message": message,
        "success": False
    },
    SYMBOL_REQUIRED={
        "code": ReturnCodes.SYMBOL_REQUIRED,
        "success": False,
        "message": "Parameter 'symbol' is required."
    },
    SYMBOL_INVALID=lambda message: {
        "code": ReturnCodes.SYMBOL_INVALID,
        "success": False,
        "message": message
    },
    EXCHANGE_REQUIRED={
        "code": ReturnCodes.EXCHANGE_REQUIRED,
        "success": False,
        "message": "Parameter 'exchange' is required."
    },
    EXCHANGE_INVALID=lambda exchange: {
        "code": ReturnCodes.EXCHANGE_INVALID,
        "success": False,
        "message": f"{exchange} is not a valid exchange."
    },
    SIGNAL_REQUIRED=lambda message: {
        "code": ReturnCodes.SIGNAL_REQUIRED,
        "success": False,
        "message": message
    },
    SIGNAL_INVALID=lambda message: {
        "code": ReturnCodes.SIGNAL_INVALID,
        "success": False,
        "message": message
    },
    ORDER_EXECUTION_SUCCESS=lambda symbol: {
        "code": ReturnCodes.ORDER_EXECUTION_SUCCESS,
        "success": True,
        "message": f"{symbol}: Order was sent successfully.",
    },
    EQUITY_REQUIRED=lambda message: {
        "code": ReturnCodes.EQUITY_REQUIRED,
        "success": False,
        "message": message,
    },
    API_ERROR=lambda symbol, message: {
        "code": ReturnCodes.API_ERROR,
        "success": False,
        "message": message,
    },
    SYMBOL_ALREADY_TRADED=lambda message: {
        "code": ReturnCodes.SYMBOL_ALREADY_TRADED,
        "success": False,
        "message":  message
    },
    SYMBOL_NOT_BEING_TRADED=lambda message: {
        "code": ReturnCodes.SYMBOL_NOT_BEING_TRADED,
        "success": False,
        "message":  message
    },
    LEVERAGE_SETTING_FAILURE=lambda message: {
        "code": ReturnCodes.LEVERAGE_SETTING_FAILURE,
        "success": False,
        "message":  message
    },
    NEGATIVE_EQUITY=lambda message: {
        "code": ReturnCodes.NEGATIVE_EQUITY,
        "success": False,
        "message":  message
    },
)
