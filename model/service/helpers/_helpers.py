import os

APP_NAME = os.getenv("APP_NAME")

EXECUTION_APP_ENDPOINTS = {
    "EXECUTE_ORDER": lambda host_url: f"{host_url}/execute_order",
}


def convert_signal_to_text(signal):
    if signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    else:
        return "NEUTRAL"
