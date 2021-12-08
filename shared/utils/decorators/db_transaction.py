import functools
import logging

from requests import ReadTimeout, ConnectionError


def retry_failed_connection(_func=None, *, num_times=3):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
