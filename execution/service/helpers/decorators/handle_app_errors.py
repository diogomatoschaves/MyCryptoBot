import functools
import logging

from flask import jsonify

from execution.service.helpers.exceptions import *
from shared.utils.exceptions import SymbolInvalid, NoSuchPipeline, EquityRequired


def handle_app_errors(_func=None):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            from execution.service.helpers.responses import Responses

            try:
                return func(*args, **kwargs)
            except EquityRequired as e:
                logging.info(e.message)
                return jsonify(Responses.EQUITY_REQUIRED(e.message))
            except NoSuchPipeline as e:
                logging.info(e.message)
                return jsonify(Responses.NO_SUCH_PIPELINE(e.message))
            except PipelineNotActive as e:
                logging.info(e.message)
                return jsonify(Responses.PIPELINE_NOT_ACTIVE(e.message))
            except SymbolInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.SYMBOL_INVALID(e.message))
            except SymbolAlreadyTraded as e:
                logging.info(e.message)
                return jsonify(Responses.SYMBOL_ALREADY_TRADED(e.message))
            except SymbolNotBeingTraded as e:
                logging.info(e.message)
                return jsonify(Responses.SYMBOL_NOT_BEING_TRADED(e.message))
            except SignalRequired as e:
                logging.info(e.message)
                return jsonify(Responses.SIGNAL_REQUIRED(e.message))
            except SignalInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.SIGNAL_INVALID(e.message))
            except LeverageSettingFail as e:
                logging.info(e.message)
                return jsonify(Responses.LEVERAGE_SETTING_FAILURE(e.message))

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
