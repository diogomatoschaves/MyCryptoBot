import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest
import pytz
from binance.exceptions import BinanceAPIException
from django.db import IntegrityError, transaction
from requests import ReadTimeout

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    # importing via execution.service first avoids the app <-> trader
    # circular import (same order as test_binance_futures_trader.py)
    from execution.service.helpers.exceptions import SymbolNotBeingTraded  # noqa: F401
    from execution.exchanges.binance.futures import BinanceFuturesTrader

from database.model.models import Orders, Position
from shared.utils.tests.fixtures.models import (
    create_exchange, create_symbol, create_assets, create_pipeline,
)


def _order_fields(**overrides):
    fields = dict(
        order_id="123",
        transact_time=datetime(2023, 9, 1, tzinfo=pytz.utc),
        price=1, original_qty=1, executed_qty=1, cummulative_quote_qty=1,
        status="FILLED", type="MARKET", side="BUY",
    )
    fields.update(overrides)
    return fields


class TestOrdersUniqueness:

    def test_same_order_id_coexists_across_symbols(self, create_exchange, create_symbol):
        # identical Binance order id on two symbols used to collide on the
        # global primary key; now both rows persist
        Orders.objects.create(symbol_id="BTCUSDT", **_order_fields())
        Orders.objects.create(symbol_id="ETHUSDT", **_order_fields())

        assert Orders.objects.filter(order_id="123").count() == 2

    def test_same_order_id_coexists_live_and_mock(self, create_exchange, create_symbol):
        Orders.objects.create(symbol_id="BTCUSDT", mock=False, **_order_fields())
        Orders.objects.create(symbol_id="BTCUSDT", mock=True, **_order_fields())

        assert Orders.objects.filter(order_id="123").count() == 2

    def test_true_duplicate_still_rejected(self, create_exchange, create_symbol):
        Orders.objects.create(symbol_id="BTCUSDT", mock=False, **_order_fields())

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Orders.objects.create(symbol_id="BTCUSDT", mock=False, **_order_fields())


ORDER = {
    "orderId": 1,
    "clientOrderId": "abc",
    "symbol": "BTCUSDT",
    "status": "FILLED",
}


def api_exception(code, msg="error"):
    response = MagicMock()
    response.text = json.dumps({"code": code, "msg": msg})
    return BinanceAPIException(response, 400, response.text)


@pytest.fixture
def trader(mocker):
    mocker.patch(
        "execution.exchanges.binance.futures._trading.time.sleep"
    )
    return BinanceFuturesTrader(paper_trading=True)


class TestPlaceOrderIdempotent:

    def test_returns_existing_order_after_timeout(self, trader, mocker):
        """The create request timed out but had reached Binance: the order is
        found by client id and must NOT be placed a second time."""
        create = mocker.patch.object(
            trader, "futures_create_order", side_effect=ReadTimeout
        )
        mocker.patch.object(trader, "futures_get_order", return_value=ORDER)

        order = trader._place_order_idempotent(
            symbol="BTCUSDT", newClientOrderId="abc", side="BUY"
        )

        assert order == ORDER
        assert create.call_count == 1

    def test_replaces_order_when_not_found(self, trader, mocker):
        """The create request timed out before reaching Binance: re-placing
        with the same client order id is safe."""
        create = mocker.patch.object(
            trader, "futures_create_order", side_effect=[ReadTimeout, ORDER]
        )
        mocker.patch.object(
            trader, "futures_get_order", side_effect=api_exception(-2013)
        )

        order = trader._place_order_idempotent(
            symbol="BTCUSDT", newClientOrderId="abc", side="BUY"
        )

        assert order == ORDER
        assert create.call_count == 2
        assert all(
            call.kwargs["newClientOrderId"] == "abc"
            for call in create.call_args_list
        )

    def test_raises_after_exhausted_retries(self, trader, mocker):
        """Persistent connection failure must surface as an exception - never
        as a silent None that callers would record as success."""
        create = mocker.patch.object(
            trader, "futures_create_order", side_effect=ReadTimeout
        )
        mocker.patch.object(
            trader, "futures_get_order", side_effect=api_exception(-2013)
        )

        with pytest.raises(ReadTimeout):
            trader._place_order_idempotent(
                symbol="BTCUSDT", newClientOrderId="abc", side="BUY", num_times=2
            )

        assert create.call_count == 3

    def test_unknown_status_does_not_replace(self, trader, mocker):
        """If the status check itself fails for any reason other than
        order-does-not-exist, the outcome is unknown - re-placing could
        double the position, so the error must propagate."""
        create = mocker.patch.object(
            trader, "futures_create_order", side_effect=ReadTimeout
        )
        mocker.patch.object(
            trader, "futures_get_order", side_effect=api_exception(-1003)
        )

        with pytest.raises(BinanceAPIException):
            trader._place_order_idempotent(
                symbol="BTCUSDT", newClientOrderId="abc", side="BUY"
            )

        assert create.call_count == 1


class TestExecuteOrderKwargs:

    def test_internal_kwargs_not_forwarded_to_binance(self, trader, mocker):
        """reducing/stop_trading/pipeline_id are internal flags and must not
        leak into the Binance API request; closing orders are reduce-only."""
        trader.symbols["BTCUSDT"] = {
            "base": "BTC", "quote": "USDT",
            "price_precision": 2, "quantity_precision": 3,
        }
        mocker.patch(
            "execution.exchanges.binance.futures._trading.get_pipeline_data",
            return_value=None,
        )
        mocker.patch.object(
            trader, "_process_order", return_value={"executed_qty": "1"}
        )
        place = mocker.patch.object(
            trader, "_place_order_idempotent", return_value=ORDER
        )

        trader._execute_order(
            "BTCUSDT", "MARKET", "SELL", "GOING SHORT",
            units=1, reducing=True, stop_trading=True, pipeline_id=11,
        )

        kwargs = place.call_args.kwargs
        for internal in ("reducing", "stop_trading", "pipeline_id"):
            assert internal not in kwargs
        assert kwargs["reduceOnly"] is True
        assert kwargs["newClientOrderId"].startswith("11-")
        assert len(kwargs["newClientOrderId"]) <= 36


class TestPositionUniqueness:

    def test_one_position_per_pipeline(self, create_pipeline):
        Position.objects.create(pipeline_id=1, position=1)

        # the racy exists-then-create path can no longer produce a second
        # position row for the same pipeline
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Position.objects.create(pipeline_id=1, position=-1)
