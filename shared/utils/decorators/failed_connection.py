import functools
import logging

from binance.exceptions import BinanceAPIException
from requests import ReadTimeout, ConnectionError


def retry_failed_connection(_func=None, *, num_times=2):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    logging.warning(e)
                except ReadTimeout as e:
                    logging.warning(e)

                if retries <= num_times:
                    retries += 1
                    continue

                break

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
