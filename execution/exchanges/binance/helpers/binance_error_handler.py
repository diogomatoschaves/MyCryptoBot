import functools
import logging

from binance.exceptions import BinanceAPIException
from flask import jsonify

from shared.utils.helpers import get_pipeline_data


def binance_error_handler(_func=None, *, request_obj=None, num_times=3):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BinanceAPIException as e:
                logging.warning(e)

                symbol = ""
                if request_obj is not None:
                    pipeline_id = request_obj.get_json(force=True).get("pipeline_id", None)
                    pipeline_exists, pipeline = get_pipeline_data(pipeline_id)
                    symbol = pipeline.symbol

                from execution.service.helpers.responses import Responses
                return jsonify(Responses.API_ERROR(symbol, e.message))

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
