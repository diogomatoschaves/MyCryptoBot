import functools

from flask import jsonify

from execution.service.helpers.exceptions import *


def handle_app_errors(_func=None):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            from execution.service.helpers.responses import Responses

            try:
                return func(*args, **kwargs)
            except EquityRequired as e:
                return jsonify(Responses.EQUITY_REQUIRED(e.message))
            except NoSuchPipeline as e:
                return jsonify(Responses.NO_SUCH_PIPELINE(e.message))
            except PipelineNotActive as e:
                return jsonify(Responses.PIPELINE_NOT_ACTIVE(e.message))
            except SymbolInvalid as e:
                return jsonify(Responses.SYMBOL_INVALID(e.message))
            except SymbolAlreadyTraded as e:
                return jsonify((Responses.SYMBOL_ALREADY_TRADED(e.message)))
            except SymbolNotBeingTraded as e:
                return jsonify((Responses.SYMBOL_NOT_BEING_TRADED(e.message)))
            except SignalRequired as e:
                return jsonify(Responses.SIGNAL_REQUIRED(e.message))
            except SignalInvalid as e:
                return jsonify(Responses.SIGNAL_INVALID(e.message))

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
