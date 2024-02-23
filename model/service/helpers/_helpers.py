import os

from shared.utils.helpers import get_root_dir

APP_NAME = os.getenv("APP_NAME")

EXECUTION_APP_ENDPOINTS = {
    "EXECUTE_ORDER": lambda host_url: f"{host_url}/execute_order",
}
STRATESTIC_STRATEGIES_LOCATION = "stratestic.strategies"
LOCAL_STRATEGIES_LOCATION = "model.strategies"
LOCAL_MODELS_LOCATION = get_root_dir() + "/model/strategies/models"
