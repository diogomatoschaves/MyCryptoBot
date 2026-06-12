import functools
import logging
import os

import django
from binance.exceptions import BinanceAPIException

from execution.service.helpers.exceptions import SymbolNotBeingTraded, NegativeEquity
from shared.utils.notifier import send_alert

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline


def stop_symbol_trading(trader_instance, pipeline_id, symbol, header):
    try:
        trader_instance.stop_symbol_trading(pipeline_id, symbol, header=header)
    except SymbolNotBeingTraded:
        pass


def deactivate_pipeline(pipeline_id):
    Pipeline.objects.filter(id=pipeline_id).update(active=False)


def handle_order_execution_errors(symbol, trader_instance, header, pipeline_id):
    """
    Handles fatal errors from a trade execution.

    The wrapped call is made exactly once: transient connection errors are
    retried at the single-order level (`_place_order_idempotent`) with an
    idempotency key, so re-invoking the whole trade here would re-run order
    placement and bookkeeping from a half-mutated state and could duplicate
    orders. Connection errors are deliberately not caught - the caller (and
    ultimately the data service's failure counter) decides how to react to an
    unreachable exchange.

    A `BinanceAPIException` at this level is a real API rejection (insufficient
    margin, invalid quantity, ...) that retrying with identical arguments
    cannot fix: the position is closed and the pipeline deactivated so the
    data service stops sending signals into a broken trading state.
    """
    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func()
            except BinanceAPIException as e:
                logging.warning(e.message)

                stop_symbol_trading(trader_instance, pipeline_id, symbol, header)
                deactivate_pipeline(pipeline_id)

                send_alert(
                    title="Pipeline deactivated by exchange error",
                    body=(
                        f"Pipeline {pipeline_id} ({symbol}): Binance rejected the "
                        f"operation ({e.message}). The position was closed and the "
                        f"pipeline deactivated."
                    ),
                    severity="critical",
                    dedup_key=f"deactivated-{pipeline_id}",
                )

                from execution.service.helpers.responses import Responses

                return Responses.API_ERROR(symbol, e.message)

            except NegativeEquity as e:
                logging.warning(e.message)

                stop_symbol_trading(trader_instance, pipeline_id, symbol, header)
                deactivate_pipeline(pipeline_id)

                send_alert(
                    title="Pipeline deactivated - negative equity",
                    body=(
                        f"Pipeline {pipeline_id} ({symbol}): {e.message} The position "
                        f"was closed and the pipeline deactivated."
                    ),
                    severity="critical",
                    dedup_key=f"deactivated-{pipeline_id}",
                )

                from execution.service.helpers.responses import Responses

                return Responses.NEGATIVE_EQUITY(e.message)

        return wrapper
    return decorator
