from unittest.mock import MagicMock

import pytest
from requests import ConnectionError as RequestsConnectionError

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from execution.service.reconciliation import reconcile_positions

from database.model.models import Pipeline, Position, Trade
from execution.tests.setup.fixtures.internal_modules import mock_redis_connection  # noqa: F401
from shared.utils.tests.fixtures.models import (  # noqa: F401
    create_exchange, create_symbol, create_assets, create_pipeline,
)


MARK_PRICE = 120.0


def make_trader(position_amt, quantity_precision=3):
    trader = MagicMock()
    trader._get_position_amt.return_value = position_amt
    trader.validate_symbol.return_value = MagicMock(quantity_precision=quantity_precision)
    trader.futures_symbol_ticker.return_value = {"price": str(MARK_PRICE)}
    trader.futures_account_balance.return_value = [
        {"asset": "USDT", "balance": "1000", "availableBalance": "800"}
    ]
    return trader


@pytest.fixture
def mock_alert(mocker):
    return mocker.patch("execution.service.reconciliation.send_alert")


@pytest.mark.django_db
class TestReconcilePositions:

    def test_corrects_pipeline_when_exchange_has_more(
        self, create_pipeline, mock_alert
    ):
        # fixture pipeline: units=0.3, no Position row
        trader = make_trader(position_amt=0.5)

        reconcile_positions(lambda paper_trading: trader)

        pipeline = Pipeline.objects.get(id=1)
        assert pipeline.units == 0.5

        position = Position.objects.get(pipeline_id=1)
        assert position.position == 1
        assert position.amount == 0.5

        trade = Trade.objects.get(pipeline_id=1)
        assert trade.close_time is None
        assert trade.side == 1

        mock_alert.assert_called_once()
        assert mock_alert.call_args.kwargs["severity"] == "critical"
        assert "0.3" in mock_alert.call_args.kwargs["body"]
        assert "0.5" in mock_alert.call_args.kwargs["body"]

    def test_flattens_pipeline_when_exchange_is_flat(
        self, create_pipeline, mock_alert
    ):
        Position.objects.create(
            pipeline_id=1, position=1, amount=0.3, buying_price=100.0
        )
        Trade.objects.create(
            pipeline_id=1, open_price=100.0, amount=0.3, side=1
        )
        trader = make_trader(position_amt=0.0)

        reconcile_positions(lambda paper_trading: trader)

        pipeline = Pipeline.objects.get(id=1)
        assert pipeline.units == 0.0

        position = Position.objects.get(pipeline_id=1)
        assert position.position == 0
        assert position.amount is None

        trade = Trade.objects.get(pipeline_id=1)
        assert trade.close_time is not None
        assert trade.close_price == MARK_PRICE
        assert trade.pnl == pytest.approx((MARK_PRICE - 100.0) * 0.3)

        mock_alert.assert_called_once()

    def test_within_tolerance_is_noop(self, create_pipeline, mock_alert):
        # quantity_precision=3 -> tolerance 0.001; diff of 0.0004 is noise
        trader = make_trader(position_amt=0.3004)

        reconcile_positions(lambda paper_trading: trader)

        assert Pipeline.objects.get(id=1).units == 0.3
        assert not Position.objects.filter(pipeline_id=1).exists()
        mock_alert.assert_not_called()

    def test_missing_exchange_entry_treated_as_flat(self, create_pipeline, mock_alert):
        trader = make_trader(position_amt=None)

        reconcile_positions(lambda paper_trading: trader)

        assert Pipeline.objects.get(id=1).units == 0.0
        mock_alert.assert_called_once()

    def test_multiple_pipelines_on_symbol_alert_only(self, create_pipeline, mock_alert):
        Pipeline.objects.create(
            id=2, name="Second", symbol_id="BTCUSDT", exchange_id="binance",
            interval="1h", active=True, initial_equity=1000, leverage=1,
            balance=0, units=0.2,
        )
        trader = make_trader(position_amt=0.9)  # != 0.3 + 0.2

        reconcile_positions(lambda paper_trading: trader)

        # no auto-correction: attribution would be a guess
        assert Pipeline.objects.get(id=1).units == 0.3
        assert Pipeline.objects.get(id=2).units == 0.2
        mock_alert.assert_called_once()
        assert "Unattributable" in mock_alert.call_args.kwargs["title"]

    def test_paper_pipeline_uses_paper_trader(self, create_pipeline, mock_alert):
        Pipeline.objects.filter(id=1).update(paper_trading=True)

        live_trader = make_trader(position_amt=0.3)
        paper_trader = make_trader(position_amt=0.3)
        traders = {True: paper_trader, False: live_trader}

        reconcile_positions(lambda paper_trading: traders[paper_trading])

        paper_trader._get_position_amt.assert_called_once_with("BTCUSDT")
        live_trader._get_position_amt.assert_not_called()

    def test_exchange_error_falls_back_without_raising(self, create_pipeline, mock_alert):
        Pipeline.objects.create(
            id=2, name="Other", symbol_id="ETHUSDT", exchange_id="binance",
            interval="1h", active=True, initial_equity=1000, leverage=1,
            balance=0, units=0.0, paper_trading=True,
        )

        failing_trader = make_trader(position_amt=None)
        failing_trader._get_position_amt.side_effect = RequestsConnectionError("down")
        ok_trader = make_trader(position_amt=2.0)
        traders = {False: failing_trader, True: ok_trader}

        reconcile_positions(lambda paper_trading: traders[paper_trading])

        # the failing live group fell back to DB state...
        assert Pipeline.objects.get(id=1).units == 0.3
        # ...while the healthy paper group was still reconciled
        assert Pipeline.objects.get(id=2).units == 2.0

        titles = [call.kwargs["title"] for call in mock_alert.call_args_list]
        assert "Position reconciliation failed" in titles
        assert "Pipeline position reconciled" in titles


@pytest.mark.django_db
class TestStartupTask:

    def test_starts_active_pipelines_without_position_rows(
        self, mocker, mock_redis_connection, create_pipeline
    ):
        # the old startup iterated Position rows, silently skipping active
        # pipelines that had none; iterating pipelines closes that gap
        import execution.service.app as app_module

        mocker.patch.object(app_module, "start_background_scheduler")
        reconcile = mocker.patch.object(app_module, "reconcile_positions")
        start = mocker.patch.object(app_module, "start_pipeline_trade")

        app_module.startup_task()

        reconcile.assert_called_once()
        assert start.call_count == 1
        assert start.call_args.args[0].id == 1
