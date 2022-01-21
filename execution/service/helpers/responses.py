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
        "ORDER_EXECUTION_SUCCESS"
    ]
)


Responses = RESPONSES(
    TRADING_SYMBOL_START=lambda symbol: {
        "success": True,
        "message": f"{symbol}: Trading symbol successfully started."
    },
    TRADING_SYMBOL_NO_ACCOUNT=lambda symbol: {
        "success": False,
        "message":  f"{symbol}: Trading account does not exist."
    },
    TRADING_SYMBOL_STOP=lambda symbol: {
        "success": True,
        "message": f"{symbol}: Trading symbol successfully stopped."
    },
    PIPELINE_NOT_ACTIVE=lambda symbol, pipeline_id: {
        "success": False,
        "message":  f"{symbol}: Pipeline {pipeline_id} not active."
    },
    NO_SUCH_PIPELINE=lambda pipeline_id: {"message": f"Pipeline {pipeline_id} was not found.", "success": False},
    SYMBOL_REQUIRED={"success": False, "message": "A symbol must be included in the request."},
    SYMBOL_INVALID=lambda symbol: {"success": False, "message": f"{symbol} is not a valid symbol."},
    EXCHANGE_REQUIRED={"success": False, "message": "An exchange must be included in the request."},
    EXCHANGE_INVALID=lambda exchange: {"success": False, "message": f"{exchange} is not a valid exchange."},
    SIGNAL_REQUIRED={"success": False, "message": "A signal must be included in the request."},
    SIGNAL_INVALID=lambda signal: {"success": False, "message": f"{signal} is not a valid signal."},
    ORDER_EXECUTION_SUCCESS=lambda symbol: {"message": f"{symbol}: Order was sent successfully.", "success": True},
)
