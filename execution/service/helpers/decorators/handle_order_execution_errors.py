import functools
import logging

from binance.exceptions import BinanceAPIException


def handle_order_execution_errors(symbol, trader_instance, header, num_times=3):

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

                    trader_instance.stop_symbol_trading(symbol=symbol, header=header)

                    message = e.message
                    logging.warning(message)

                    from execution.service.helpers.responses import Responses

                    return Responses.API_ERROR(symbol, message)

        return wrapper
    return decorator
