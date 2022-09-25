from collections import namedtuple


RESPONSES = namedtuple(
    'Responses',
    [
        "TRADING_SYMBOL_START",
        "TRADING_SYMBOL_NO_ACCOUNT",
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
        "EQUITY_REQUIRED"
    ]
)


ReturnCodes = RESPONSES(
    TRADING_SYMBOL_START="TRADING_SYMBOL_START",
    TRADING_SYMBOL_NO_ACCOUNT="TRADING_SYMBOL_NO_ACCOUNT",
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
    EQUITY_REQUIRED="EQUITY_REQUIRED"
)


Responses = RESPONSES(
    TRADING_SYMBOL_START=lambda symbol: {
        "code": ReturnCodes.TRADING_SYMBOL_START,
        "success": True,
        "message": f"{symbol}: Trading symbol successfully started."
    },
    TRADING_SYMBOL_NO_ACCOUNT=lambda symbol: {
        "code": ReturnCodes.TRADING_SYMBOL_NO_ACCOUNT,
        "success": False,
        "message":  f"{symbol}: Trading account does not exist."
    },
    TRADING_SYMBOL_STOP=lambda symbol: {
        "code": ReturnCodes.TRADING_SYMBOL_STOP,
        "success": True,
        "message": f"{symbol}: Trading symbol successfully stopped."
    },
    PIPELINE_NOT_ACTIVE=lambda symbol, pipeline_id: {
        "code": ReturnCodes.PIPELINE_NOT_ACTIVE,
        "success": False,
        "message":  f"{symbol}: Pipeline {pipeline_id} not active."
    },
    NO_SUCH_PIPELINE=lambda pipeline_id: {
        "code": ReturnCodes.NO_SUCH_PIPELINE,
        "message": f"Pipeline {pipeline_id} was not found.",
        "success": False
    },
    SYMBOL_REQUIRED={
        "code": ReturnCodes.SYMBOL_REQUIRED,
        "success": False,
        "message": "Parameter 'symbol' is required."
    },
    SYMBOL_INVALID=lambda symbol: {
        "code": ReturnCodes.SYMBOL_INVALID,
        "success": False,
        "message": f"{symbol} is not a valid symbol."
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
    SIGNAL_REQUIRED={
        "code": ReturnCodes.SIGNAL_REQUIRED,
        "success": False,
        "message": "A signal must be included in the request."
    },
    SIGNAL_INVALID=lambda signal: {
        "code": ReturnCodes.SIGNAL_INVALID,
        "success": False,
        "message": f"{signal} is not a valid signal."
    },
    ORDER_EXECUTION_SUCCESS=lambda symbol: {
        "code": ReturnCodes.ORDER_EXECUTION_SUCCESS,
        "success": True,
        "message": f"{symbol}: Order was sent successfully.",
    },
    EQUITY_REQUIRED=lambda symbol: {
        "code": ReturnCodes.EQUITY_REQUIRED,
        "success": False,
        "message": f"{symbol}: Parameter 'equity' is required.",
    },
)
