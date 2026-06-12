import functools
import logging
import time

from binance.exceptions import BinanceAPIException
from requests import ReadTimeout, ConnectionError


def retry_failed_connection(_func=None, *, num_times=2, backoff_base=1):
    """Retries the wrapped function on connection errors with exponential
    backoff. Re-raises the last exception once retries are exhausted — callers
    must not rely on a silent None return.

    Do NOT use this on non-idempotent operations (e.g. order placement):
    re-invoking after a timeout can repeat a request that already succeeded.
    """
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, ReadTimeout) as e:
                    logging.warning(e)

                    retries += 1
                    if retries > num_times:
                        raise

                    logging.debug('Retrying failed connection.')
                    time.sleep(backoff_base * 2 ** (retries - 1))

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
