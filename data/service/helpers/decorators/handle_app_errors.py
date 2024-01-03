import functools
import logging
import traceback

from flask import jsonify

from data.service.helpers.exceptions import *
from shared.utils.exceptions import SymbolInvalid, EquityRequired, EquityInvalid, StrategyInvalid, StrategyRequired


def handle_app_errors(_func=None):
    def retry(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            from data.service.helpers.responses import Responses

            try:
                return func(*args, **kwargs)
            except ExchangeInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.EXCHANGE_INVALID(e.message))
            except ExchangeRequired as e:
                logging.info(e.message)
                return jsonify(Responses.EXCHANGE_REQUIRED(e.message))
            except SymbolInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.SYMBOL_INVALID(e.message))
            except SymbolRequired as e:
                logging.info(e.message)
                return jsonify(Responses.SYMBOL_REQUIRED(e.message))
            except CandleSizeInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.CANDLE_SIZE_INVALID(e.message))
            except CandleSizeRequired as e:
                logging.info(e.message)
                return jsonify(Responses.CANDLE_SIZE_REQUIRED(e.message))
            except StrategyInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.STRATEGY_INVALID(e.message))
            except StrategyRequired as e:
                logging.info(e.message)
                return jsonify(Responses.STRATEGY_REQUIRED(e.message))
            except ParamsInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.PARAMS_INVALID(e.message))
            except ParamsRequired as e:
                logging.info(e.message)
                return jsonify(Responses.PARAMS_REQUIRED(e.message))
            except NameInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.NAME_INVALID(e.message))
            except NameRequired as e:
                logging.info(e.message)
                return jsonify(Responses.NAME_REQUIRED(e.message))
            except ColorRequired as e:
                logging.info(e.message)
                return jsonify(Responses.COLOR_REQUIRED(e.message))
            except DataPipelineOngoing as e:
                logging.info(e.message)
                return jsonify(Responses.DATA_PIPELINE_ONGOING(e.message, e.pipeline_id))
            except DataPipelineDoesNotExist as e:
                logging.info(e.message)
                return jsonify(Responses.DATA_PIPELINE_DOES_NOT_EXIST(e.message))
            except DataPipelineCouldNotBeStopped as e:
                logging.info(e.message)
                return jsonify(Responses.DATA_PIPELINE_COULD_NOT_BE_STOPPED(e.message))
            except LeverageInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.LEVERAGE_INVALID(e.message))
            except PipelineStartFail as e:
                logging.info(e.message)
                return jsonify(Responses.PIPELINE_START_FAIL(e.message))
            except EquityInvalid as e:
                logging.info(e.message)
                return jsonify(Responses.EQUITY_INVALID(e.message))
            except EquityRequired as e:
                logging.info(e.message)
                return jsonify(Responses.EQUITY_REQUIRED(e.message))
            finally:
                logging.error(traceback.format_exc())

        return wrapper

    if _func is None:
        return retry
    else:
        return retry(_func)
