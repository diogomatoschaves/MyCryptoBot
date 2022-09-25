import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Orders, Position, Trade
from execution.exchanges.binance.margin import BinanceMarginTrader
from execution.tests.setup.fixtures.external_modules import *
from shared.utils.tests.fixtures.models import *


def inject_fixture(mock_name, method):
    globals()[f"{mock_name}"] = binance_client_mock_factory(method)
    globals()[f"{mock_name}_spy"] = binance_client_mock_factory(method, 'spy')


METHODS = [
    ("init_session", "_init_session"),
    ("ping", "ping"),
    ("get_isolated_margin_account", "get_isolated_margin_account"),
    ("create_margin_loan", "create_margin_loan"),
    ("get_trade_fee", "get_trade_fee"),
    ("get_max_margin_loan", "get_max_margin_loan"),
    ("create_margin_order", "create_margin_order"),
    ("repay_margin_loan", "repay_margin_loan"),
]

for method in METHODS:
    inject_fixture(*method)


class TestBinanceMarginTrader:

    symbol = "BTCUSDT"

    @pytest.mark.parametrize(
        "symbol,symbols,times_called,expected_value",
        [
            pytest.param(
                "BTCUSDT",
                {},
                (1, 2, 1, 1, 1),
                True,
                id="SymbolExists-True",
            ),
            pytest.param(
                "BNBBTC",
                {},
                (0, 0, 0, 0, 0),
                False,
                id="TradingAccountDoesntExist-False",
            ),
            pytest.param(
                "BTCUSDT",
                {"BTCUSDT"},
                (0, 0, 0, 0, 0),
                True,
                id="SymbolIsAlreadyBeingTraded-True",
            ),
            pytest.param(
                "XRPBTC",
                {},
                (0, 0, 0, 0, 0),
                False,
                id="SymbolDoesNotExist-False",
            ),
        ]
    )
    def test_start_symbol_trading(
        self,
        symbol,
        symbols,
        times_called,
        expected_value,
        create_symbol,
        create_exchange,
        ping,
        init_session,
        get_isolated_margin_account,
        create_margin_loan,
        get_trade_fee,
        get_max_margin_loan,
        create_margin_order,
        get_isolated_margin_account_spy,
        create_margin_loan_spy,
        get_trade_fee_spy,
        get_max_margin_loan_spy,
        create_margin_order_spy
    ):
        binance_trader = BinanceMarginTrader()
        binance_trader.symbols = symbols

        return_value = binance_trader.start_symbol_trading(symbol)

        assert return_value == expected_value

        assert get_trade_fee_spy.call_count == times_called[0]
        assert get_max_margin_loan_spy.call_count == times_called[1]
        assert create_margin_loan_spy.call_count == times_called[2]
        assert get_isolated_margin_account_spy.call_count >= times_called[3]
        assert create_margin_order_spy.call_count >= times_called[4]

    @pytest.mark.parametrize(
        "symbols,units,times_called,expected_value",
        [
            pytest.param(
                {"BTCUSDT": {"quote": "USDT", "base": "BTC"}},
                0.1,
                (2, 1),
                True,
                id="SymbolExists-PositiveUnits-True",
            ),
            pytest.param(
                {"BTCUSDT": {"quote": "USDT", "base": "BTC"}},
                -0.1,
                (2, 1),
                True,
                id="SymbolExists-NegativeUnits-True",
            ),
            pytest.param(
                {},
                0.1,
                (0, 0),
                False,
                id="SymbolDoesNotExist-False",
            ),
            pytest.param(
                {"BTCUSDT": {"quote": "USDT", "base": "BTC"}},
                0,
                (2, 0),
                False,
                id="NoUnits-False",
            ),
        ]
    )
    def test_stop_symbol_trading(
        self,
        symbols,
        units,
        times_called,
        expected_value,
        create_symbol,
        create_exchange,
        create_orders,
        ping,
        init_session,
        create_margin_order,
        create_margin_order_spy,
        repay_margin_loan,
        repay_margin_loan_spy
    ):
        binance_trader = BinanceMarginTrader()
        binance_trader.symbols = symbols

        binance_trader._set_position(self.symbol, 1, pipeline_id=1)
        binance_trader.units = units
        binance_trader.initial_balance = 100
        binance_trader.max_borrow_amount = {
            self.symbol: {
                "BTC": "60", "USDT": "1000"
            }
        }

        return_value = binance_trader.stop_symbol_trading(self.symbol, pipeline_id=1)

        assert return_value == expected_value

        assert repay_margin_loan_spy.call_count == times_called[0]
        assert create_margin_order_spy.call_count == times_called[1]

    @pytest.mark.parametrize("signal", [-1, 0, 1])
    @pytest.mark.parametrize("initial_position", [-1, 0, 1])
    def test_trade(
        self,
        initial_position,
        signal,
        ping,
        init_session,
        create_symbol,
        create_exchange,
        create_orders,
        create_margin_order,
        create_margin_order_spy,
        create_pipeline
    ):
        binance_trader = BinanceMarginTrader()
        binance_trader.symbols = {
            self.symbol: {
                "quote": "USDT", "base": "BTC"
            }
        }

        pipeline_id = 1

        print(f"initial_position: {initial_position}, signal: {signal}")

        binance_trader._set_position(self.symbol, initial_position, pipeline_id=pipeline_id)

        binance_trader.trade(self.symbol, signal, amount="all", pipeline_id=pipeline_id)

        assert binance_trader._get_position(self.symbol) == signal

        number_orders = abs(initial_position - signal)

        assert create_margin_order_spy.call_count == number_orders

        if number_orders > 0:
            order = Orders.objects.last()
            assert order.pipeline_id == pipeline_id

            positions = Position.objects.all()

            assert len(positions) == 1
            assert positions[0].position == signal
            assert positions[0].open if signal != 0 else not positions[0].open

        if initial_position == 0 and signal == 0:
            assert Trade.objects.all().count() == 0
        else:
            trades = Trade.objects.all()

            assert len(trades) == max(number_orders, 1)
            assert trades[0].amount == float(margin_order_creation["executedQty"])
            assert trades[0].open_price == float(margin_order_creation["price"])

    def test_all(
        self,
        ping,
        init_session,
        create_symbol,
        create_exchange,
        create_pipeline,
        create_orders,
        create_margin_order,
        repay_margin_loan,
        get_isolated_margin_account,
        create_margin_loan,
        get_trade_fee,
        get_max_margin_loan,
    ):

        binance_trader = BinanceMarginTrader()

        binance_trader.start_symbol_trading(self.symbol, pipeline_id=1)
        binance_trader.trade(self.symbol, 1, amount="all", pipeline_id=1)
        binance_trader.stop_symbol_trading(self.symbol, pipeline_id=1)

        positions = Position.objects.all()

        assert len(positions) == 1
        assert positions[0].position == 0
        assert not positions[0].open

        trades = Trade.objects.all()

        assert len(trades) == 1
        assert all(trade.amount == float(margin_order_creation["executedQty"]) for trade in trades)
        assert all(trade.open_price == float(margin_order_creation["price"]) for trade in trades)
