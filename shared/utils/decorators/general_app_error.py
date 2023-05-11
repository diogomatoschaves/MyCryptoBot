import functools
import logging
import sys
import traceback


def general_app_error(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(traceback.format_exc())

            return sys.exit(0)

    return wrapper
