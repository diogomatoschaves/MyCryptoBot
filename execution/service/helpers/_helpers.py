import json
import os
from collections import namedtuple

import django
import redis

from execution.service.helpers.exceptions import SignalRequired, SignalInvalid
from shared.utils.config_parser import get_config
from shared.utils.exceptions import NoSuchPipeline
from shared.utils.helpers import get_pipeline_data, get_item_from_cache

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

config_vars = get_config('execution')

cache = redis.from_url(os.getenv('REDIS_URL', config_vars.redis_url))

fields = [
    "header",
    "force",
    "paper_trading",
    "symbol",
    "signal",
    "amount"
]

Parameters = namedtuple(
    'Parameters',
    fields,
    defaults=(None,) * len(fields)
)


def validate_signal(signal):
    """
    Validates the trading signal to ensure it is one of the accepted values.

    Parameters
    ----------
    signal : int
        The trading signal to be validated. Accepted values are -1, 0, 1, where -1 indicates a sell signal,
        1 indicates a buy signal, and 0 indicates no action.

    Raises
    ------
    SignalRequired
        If the `signal` parameter is None, indicating that a signal was expected but not provided.
    SignalInvalid
        If the `signal` parameter is not one of the accepted values (-1, 0, 1).

    Notes
    -----
    This function is used to ensure that only valid signals are processed by the trading system,
    preventing errors or unintended actions.
    """
    if signal is None:
        raise SignalRequired

    if signal not in [-1, 0, 1]:
        raise SignalInvalid(signal)


def get_header(pipeline_id):
    """
    Retrieves the header information for a given pipeline from the Redis cache.

    Parameters
    ----------
    pipeline_id : str or int
        The identifier of the trading pipeline for which to retrieve header information.

    Returns
    -------
    dict
        A dictionary containing the header information for the specified pipeline.

    Notes
    -----
    This function assumes that header information for each pipeline is stored in
    Redis cache in a serialized (JSON) format.
    The function deserializes this information into a Python dictionary before returning it.
    """
    return json.loads(get_item_from_cache(cache, pipeline_id))


def extract_and_validate(request_data):
    """
    Extracts trading parameters from a request and validates them, including checking for
    the existence of a corresponding pipeline.

    Parameters
    ----------
    request_data : dict
        A dictionary containing data from a trading request. Expected keys are "pipeline_id", "force",
        "paper_trading", and "symbol".

    Returns
    -------
    tuple
        A tuple containing the pipeline object (if found) and a namedtuple `Parameters` with extracted values.

    Raises
    ------
    NoSuchPipeline
        If no pipeline is found for the given `pipeline_id` and either `paper_trading` is None or `symbol` is None.

    Notes
    -----
    This function performs several key steps:
    - Extracts parameters from the request data.
    - Attempts to retrieve the corresponding pipeline using `get_pipeline_data`.
    - Validates that the necessary parameters are provided, raising `NoSuchPipeline` if the validation fails.
    - Constructs a `Parameters` namedtuple with the extracted values for easy access.
    """

    pipeline_id = request_data.get("pipeline_id", None)
    force = request_data.get("force", False)
    paper_trading = request_data.get("paper_trading", None)
    symbol = request_data.get("symbol", None)
    signal = request_data.get("signal", None)
    amount = request_data.get("amount", "all")

    pipeline = get_pipeline_data(pipeline_id, return_obj=True, ignore_exception=force)

    if pipeline is None and (paper_trading is None or symbol is None):
        raise NoSuchPipeline(pipeline_id)

    header = get_header(pipeline_id)

    return pipeline, Parameters(header, force, paper_trading, symbol, signal, amount)
