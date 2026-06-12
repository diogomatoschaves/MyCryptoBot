"""
Startup reconciliation of local position records against the exchange.

The execution service's in-memory state and the Position/Trade/Pipeline rows
can lag the exchange when the process dies between an exchange fill and the
local bookkeeping (the bookkeeping is atomic, but the exchange call happens
first by necessity). On startup the exchange is treated as the source of
truth: each active pipeline's recorded units are compared against the actual
exchange position and corrected when they diverge.

Limitations (v1, by design):
- Binance reports one position per (symbol, account). When several active
  pipelines trade the same symbol on the same account, a mismatch cannot be
  attributed to any one of them — it is alerted, never auto-corrected.
- Balance/equity are NOT auto-corrected: the fill prices of the missing
  delta are unknown. The alert includes the account balance so the operator
  can adjust `current_equity` manually if needed.
- Corrected prices (`buying_price`, dangling-trade close price) use the
  current mark price, which is approximate; alerts flag this.
"""

import logging
import os
from collections import defaultdict
from datetime import datetime

import django
import pytz
from django.db import transaction

from shared.utils.notifier import send_alert

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Pipeline, Position, Trade, Orders


def _account_name(paper_trading):
    return "testnet" if paper_trading else "LIVE"


def _quantity_tolerance(trader, symbol):
    try:
        return 10 ** -trader.validate_symbol(symbol).quantity_precision
    except Exception:
        return 1e-8


def _mark_price(trader, symbol):
    return float(trader.futures_symbol_ticker(symbol=symbol)["price"])


def reconcile_positions(get_trader_instance):
    """
    Compares every active pipeline's recorded units with the actual exchange
    position and corrects the records (exchange wins) where the mismatch is
    attributable to a single pipeline.

    Parameters
    ----------
    get_trader_instance : callable
        Returns the trader instance for a given paper_trading flag, so live
        and testnet pipelines are each checked against their own account.

    Never raises: a failure to reconcile one (symbol, account) group falls
    back to the existing DB state for that group and alerts, so startup
    always proceeds.
    """
    groups = defaultdict(list)

    for pipeline in Pipeline.objects.filter(active=True).select_related("symbol"):
        if pipeline.symbol is None:
            continue
        groups[(pipeline.paper_trading, pipeline.symbol.name)].append(pipeline)

    for (paper_trading, symbol), pipelines in groups.items():
        account = _account_name(paper_trading)

        try:
            trader = get_trader_instance(paper_trading)

            actual = trader._get_position_amt(symbol)
            if actual is None:
                logging.info(
                    f"No exchange position entry for {symbol} ({account}); treating as flat."
                )
                actual = 0.0

            expected = sum(pipeline.units for pipeline in pipelines)
            tolerance = _quantity_tolerance(trader, symbol)

            if abs(actual - expected) <= tolerance:
                continue

            if len(pipelines) == 1:
                _correct_pipeline(trader, pipelines[0], actual, account)
            else:
                pipeline_ids = [pipeline.id for pipeline in pipelines]
                send_alert(
                    title="Unattributable position mismatch",
                    body=(
                        f"{symbol} ({account}): exchange position is {actual}, "
                        f"DB pipelines sum to {expected} across pipelines "
                        f"{pipeline_ids}. Multiple pipelines share this symbol - "
                        f"not auto-correcting. Verify on the exchange and fix the "
                        f"pipeline records manually."
                    ),
                    severity="critical",
                    dedup_key=f"reconcile-multi-{account}-{symbol}",
                )

        except Exception as e:
            logging.error(f"Reconciliation failed for {symbol} ({account}): {e}")
            send_alert(
                title="Position reconciliation failed",
                body=(
                    f"{symbol} ({account}): could not verify the exchange position "
                    f"({e}). Falling back to the local records for this symbol."
                ),
                severity="warning",
                dedup_key=f"reconcile-error-{account}-{symbol}",
            )


def _correct_pipeline(trader, pipeline, actual_amt, account):
    """
    Rewrites a single pipeline's units, Position row and dangling Trade to
    match the exchange. All writes happen in one transaction.
    """
    recorded_units = pipeline.units
    new_position = 1 if actual_amt > 0 else -1 if actual_amt < 0 else 0
    price_is_approximate = False

    with transaction.atomic():
        pipeline.units = actual_amt
        pipeline.save(update_fields=["units"])

        position_row = Position.objects.filter(pipeline_id=pipeline.id).first()

        if new_position == 0:
            if position_row:
                Position.objects.filter(pipeline_id=pipeline.id).update(
                    position=0, amount=None, buying_price=None, open_time=None
                )
            else:
                Position.objects.create(position=0, pipeline_id=pipeline.id)

            # exchange is flat: close any trade the records still hold open
            open_trade = (
                Trade.objects.filter(pipeline_id=pipeline.id, close_time__isnull=True)
                .order_by("-open_time")
                .first()
            )
            if open_trade:
                price_is_approximate = True
                open_trade.close_price = _mark_price(trader, pipeline.symbol.name)
                open_trade.close_time = datetime.now(tz=pytz.UTC)
                open_trade.pnl = open_trade.get_profit_loss()
                open_trade.pnl_pct = open_trade.get_profit_loss_pct()
                open_trade.save()

        else:
            direction_matches = (
                position_row is not None
                and position_row.position == new_position
                and position_row.buying_price is not None
            )

            if direction_matches:
                entry_price = position_row.buying_price
            else:
                last_order = (
                    Orders.objects.filter(
                        pipeline_id=pipeline.id, symbol_id=pipeline.symbol.name
                    )
                    .order_by("-transact_time")
                    .first()
                )
                if last_order is not None:
                    entry_price = last_order.price
                else:
                    price_is_approximate = True
                    entry_price = _mark_price(trader, pipeline.symbol.name)

            if position_row:
                Position.objects.filter(pipeline_id=pipeline.id).update(
                    position=new_position,
                    amount=abs(actual_amt),
                    buying_price=entry_price,
                    open_time=datetime.now(tz=pytz.UTC),
                )
            else:
                Position.objects.create(
                    position=new_position,
                    pipeline_id=pipeline.id,
                    amount=abs(actual_amt),
                    buying_price=entry_price,
                )

            # exchange holds a position the records don't know about
            has_open_trade = Trade.objects.filter(
                pipeline_id=pipeline.id, close_time__isnull=True
            ).exists()
            if not has_open_trade:
                Trade.objects.create(
                    open_price=entry_price,
                    amount=abs(actual_amt),
                    side=new_position,
                    pipeline_id=pipeline.id,
                )

    try:
        balances = trader.futures_account_balance()
    except Exception:
        balances = "unavailable"

    send_alert(
        title="Pipeline position reconciled",
        body=(
            f"Pipeline {pipeline.id} ('{pipeline.name}', {pipeline.symbol.name}, "
            f"{account}): DB recorded {recorded_units} units, exchange reports "
            f"{actual_amt}. Records were corrected to match the exchange"
            f"{' using approximate mark prices' if price_is_approximate else ''}. "
            f"Balance/equity were NOT auto-corrected - account balance: {balances}."
        ),
        severity="critical",
        dedup_key=f"reconciled-{pipeline.id}",
    )
