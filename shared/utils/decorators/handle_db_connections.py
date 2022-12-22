import functools
import logging

from django import db
from django.db import InterfaceError, OperationalError


def process_retry(retries, num_times, e, exception):

    retries += 1
    if retries > num_times:
        try:
            raise e
        except:
            raise exception()

    return retries


def handle_db_connection_error(_func=None, *, num_times=2):
    def retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except (InterfaceError, OperationalError) as e:
                    logging.warning(e)

                    for conn in db.connections.all():
                        conn.close_if_unusable_or_obsolete()

                    retries = process_retry(retries, num_times, e, InterfaceError)

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
