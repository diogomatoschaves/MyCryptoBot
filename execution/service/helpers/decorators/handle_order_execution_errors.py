import functools
import logging

from binance.exceptions import BinanceAPIException
from flask import jsonify


def handle_order_execution_errors(pipeline, trader_instance, parameters, num_times=3):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 1
            while True:
                try:
                    return func()
                except BinanceAPIException as e:

                    if retries <= num_times:
                        retries += 1
                        continue

                    logging.warning(e)

                    trader_instance.stop_symbol_trading(pipeline.symbol, header=parameters.header, pipeline_id=pipeline.id)

                    message = e.message
                    logging.warning(message)

                    from execution.service.helpers.responses import Responses

                    return jsonify(Responses.API_ERROR(pipeline.symbol, message))

        return wrapper
    return decorator
