import functools
import logging

from binance.exceptions import BinanceAPIException


def binance_error_handler(_func=None, *, num_times=3):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BinanceAPIException as e:
                logging.warning(e)
                pass

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
