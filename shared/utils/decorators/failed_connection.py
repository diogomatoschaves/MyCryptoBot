import functools
import logging

from binance.exceptions import BinanceAPIException
from requests import ReadTimeout, ConnectionError


def process_retry(retries, num_times, e, exception):
    logging.warning(e)

    retries += 1
    if retries > num_times:
        try:
            raise exception
        except TypeError:
            raise Exception(e)

    return retries


def retry_failed_connection(_func=None, *, num_times=3):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    logging.warning(e)
                    retries = process_retry(retries, num_times, e, ConnectionError)
                except ReadTimeout as e:
                    logging.warning(e)
                    retries = process_retry(retries, num_times, e, ReadTimeout)
                except BinanceAPIException as e:
                    logging.warning(e)
                    retries = process_retry(retries, num_times, e, BinanceAPIException)
        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
