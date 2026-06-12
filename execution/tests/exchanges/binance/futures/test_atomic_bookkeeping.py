import pytest
from django.db import DatabaseError
from flask import Flask

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    # importing via execution.service first avoids the app <-> trader
    # circular import (same order as test_order_idempotency.py)
    from execution.service.helpers.exceptions import BookkeepingFailed  # noqa: F401
    from execution.service.helpers.decorators import handle_app_errors
    from execution.exchanges.binance.futures import BinanceFuturesTrader

from database.model.models import Orders, Pipeline, Position, Trade
from shared.utils.tests.fixtures.models import (  # noqa: F401
    create_exchange, create_symbol, create_assets, create_pipeline,
)


FULL_ORDER = {
    "orderId": 1,
    "clientOrderId": "1-abc",
    "symbol": "BTCUSDT",
    "updateTime": 1693560000000,
    "avgPrice": "100.0",
    "origQty": "1.0",
    "executedQty": "1.0",
    "cumQuote": "100.0",
    "status": "FILLED",
    "type": "MARKET",
    "side": "SELL",
}


@pytest.fixture
def trader(mocker, create_pipeline):
    mocker.patch("execution.exchanges.binance.futures._trading.time.sleep")
    trader = BinanceFuturesTrader(paper_trading=True)
    trader.symbols["BTCUSDT"] = {
        "base": "BTC", "quote": "USDT",
        "price_precision": 2, "quantity_precision": 3,
    }
    trader.units["BTCUSDT"] = 1.0
    trader.current_balance["BTCUSDT"] = 1000.0
    trader.current_equity["BTCUSDT"] = 1000.0
    trader.initial_balance["BTCUSDT"] = 1000.0
    trader.position["BTCUSDT"] = 1

    mocker.patch.object(trader, "_place_order_idempotent", return_value=FULL_ORDER)
    mocker.patch.object(trader, "report_trade")
    mocker.patch(
        "execution.exchanges.binance.futures._trading.get_pipeline_data",
        return_value=create_pipeline,
    )
    return trader


@pytest.fixture
def mock_alert(mocker):
    return mocker.patch("execution.exchanges.binance._trading.send_alert")


@pytest.mark.django_db
class TestAtomicOrderBookkeeping:

    def test_happy_path_memory_matches_db(self, trader, create_pipeline):
        trader._execute_order(
            "BTCUSDT", "MARKET", "SELL", "GOING SHORT", units=1, pipeline_id=1
        )

        pipeline = Pipeline.objects.get(id=1)
        assert Orders.objects.count() == 1
        assert trader.units["BTCUSDT"] == pipeline.units
        assert trader.current_balance["BTCUSDT"] == pipeline.balance
        assert trader.current_equity["BTCUSDT"] == pipeline.current_equity

    def test_orders_create_failure_leaves_db_and_memory_unchanged(
        self, trader, create_pipeline, mocker, mock_alert
    ):
        mocker.patch.object(
            Orders.objects, "create", side_effect=DatabaseError("db down")
        )

        units_before = trader.units["BTCUSDT"]
        balance_before = trader.current_balance["BTCUSDT"]
        pipeline_units_before = Pipeline.objects.get(id=1).units

        with pytest.raises(BookkeepingFailed):
            trader._execute_order(
                "BTCUSDT", "MARKET", "SELL", "GOING SHORT", units=1, pipeline_id=1
            )

        assert Orders.objects.count() == 0
        assert trader.units["BTCUSDT"] == units_before
        assert trader.current_balance["BTCUSDT"] == balance_before
        assert Pipeline.objects.get(id=1).units == pipeline_units_before
        mock_alert.assert_called_once()
        assert mock_alert.call_args.kwargs["severity"] == "critical"

    def test_pipeline_save_failure_rolls_back_orders_row(
        self, trader, create_pipeline, mocker, mock_alert
    ):
        mocker.patch.object(
            Pipeline, "save", side_effect=DatabaseError("db down")
        )

        with pytest.raises(BookkeepingFailed):
            trader._execute_order(
                "BTCUSDT", "MARKET", "SELL", "GOING SHORT", units=1, pipeline_id=1
            )

        # the Orders.create succeeded inside the transaction but must have
        # been rolled back together with the failed pipeline update
        assert Orders.objects.count() == 0
        mock_alert.assert_called_once()

    def test_transient_db_error_is_retried_once(
        self, trader, create_pipeline, mocker, mock_alert
    ):
        original_create = Orders.objects.create
        calls = {"n": 0}

        def flaky_create(**kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise DatabaseError("blip")
            return original_create(**kwargs)

        mocker.patch.object(Orders.objects, "create", side_effect=flaky_create)

        trader._execute_order(
            "BTCUSDT", "MARKET", "SELL", "GOING SHORT", units=1, pipeline_id=1
        )

        assert calls["n"] == 2
        assert Orders.objects.count() == 1
        mock_alert.assert_not_called()


@pytest.mark.django_db
class TestAtomicPositionBookkeeping:

    def test_position_db_failure_keeps_memory_and_trades_unchanged(
        self, trader, create_pipeline, mocker, mock_alert
    ):
        Orders.objects.create(
            order_id="9", client_order_id="x", symbol_id="BTCUSDT",
            transact_time="2023-09-01T00:00:00Z", price=100, original_qty=1,
            executed_qty=1, cummulative_quote_qty=100, status="FILLED",
            type="MARKET", side="BUY", mock=True, pipeline_id=1,
        )
        mocker.patch.object(
            Position.objects, "create", side_effect=DatabaseError("db down")
        )

        with pytest.raises(BookkeepingFailed):
            trader._set_position("BTCUSDT", 1, previous_position=0, pipeline_id=1)

        # the Trade opened inside the transaction must have rolled back, and
        # the in-memory position must not have been touched
        assert Trade.objects.count() == 0
        assert trader.position["BTCUSDT"] == 1  # unchanged from fixture
        mock_alert.assert_called_once()

    def test_position_memory_updated_after_commit(self, trader, create_pipeline):
        trader._set_position("BTCUSDT", -1, previous_position=0, pipeline_id=1)

        assert trader.position["BTCUSDT"] == -1
        assert Position.objects.filter(pipeline_id=1, position=-1).exists()


@pytest.mark.django_db
class TestBookkeepingFailedHandler:

    def test_handler_deactivates_pipeline_and_returns_error(self, create_pipeline):
        app = Flask(__name__)

        @handle_app_errors
        def view():
            raise BookkeepingFailed(1, "order xyz")

        with app.app_context():
            response = view().get_json()

        assert response["success"] is False
        assert response["code"] == "BOOKKEEPING_FAILED"
        assert Pipeline.objects.get(id=1).active is False
