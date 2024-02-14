import functools
import logging
import sys
import traceback

from flask import Response
from jwt import ExpiredSignatureError, DecodeError


def general_app_error(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except ExpiredSignatureError as e:
            logging.debug(e)
            return Response({"msg": f"{str(e)}"}, status=422, mimetype='application/json')
        except DecodeError as e:
            logging.debug(e)
            return Response({"msg": f"{str(e)}"}, status=401, mimetype='application/json')
        except Exception as e:

            logging.warning('Error encountered. Restarting app.')

            logging.error(traceback.format_exc())

            return sys.exit(0)

    return wrapper
