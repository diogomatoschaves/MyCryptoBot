import functools
import logging

from flask import jsonify

from shared.utils.exceptions import NoSuchPipeline


def handle_app_errors(_func=None):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            from model.service.helpers.responses import Responses

            try:
                return func(*args, **kwargs)
            except NoSuchPipeline as e:
                logging.info(e.message)
                return jsonify(Responses.NO_SUCH_PIPELINE(e.message))

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
