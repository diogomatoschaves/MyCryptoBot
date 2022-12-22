import functools
import logging
from json import JSONDecodeError


def json_error_handler(_func=None):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except JSONDecodeError as e:
                logging.warning(e)
                response = {"success": False, "message": "There was an error processing the request."}

                return response, 502

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
