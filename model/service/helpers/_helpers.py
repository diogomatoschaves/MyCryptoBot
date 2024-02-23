import os

APP_NAME = os.getenv("APP_NAME")

EXECUTION_APP_ENDPOINTS = {
    "EXECUTE_ORDER": lambda host_url: f"{host_url}/execute_order",
}
