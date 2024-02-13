import functools
import logging

from binance.exceptions import BinanceAPIException

from execution.service.helpers.exceptions import SymbolNotBeingTraded, NegativeEquity


def handle_order_execution_errors(symbol, trader_instance, header, pipeline_id, num_times=3):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 1
            while True:
                try:
                    return func()
                except BinanceAPIException as e:

                    if retries <= num_times:
                        retries += 1
                        continue

                    logging.warning(e)

                    try:
                        trader_instance.stop_symbol_trading(pipeline_id, header=header)
                    except SymbolNotBeingTraded:
                        pass

                    message = e.message
                    logging.warning(message)

                    from execution.service.helpers.responses import Responses

                    return Responses.API_ERROR(symbol, message)

                except NegativeEquity as e:
                    logging.warning(e.message)

                    try:
                        trader_instance.stop_symbol_trading(pipeline_id, header=header)
                    except SymbolNotBeingTraded:
                        pass

                    from execution.service.helpers.responses import Responses

                    return Responses.NEGATIVE_EQUITY(e.message)

        return wrapper
    return decorator
