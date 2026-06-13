import functools
import json
import logging
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
            return Response(
                json.dumps({"msg": "Token has expired."}),
                status=422,
                mimetype='application/json'
            )
        except DecodeError as e:
            logging.debug(e)
            return Response(
                json.dumps({"msg": "Invalid token."}),
                status=401,
                mimetype='application/json'
            )
        except Exception:
            logging.error(traceback.format_exc())

            return Response(
                json.dumps({"msg": "Internal server error.", "success": False}),
                status=500,
                mimetype='application/json'
            )

    return wrapper
