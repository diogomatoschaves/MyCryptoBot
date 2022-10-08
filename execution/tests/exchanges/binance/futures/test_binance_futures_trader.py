import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from database.model.models import Orders, Position, Trade
from execution.exchanges.binance.futures import BinanceFuturesTrader
from execution.tests.setup.fixtures.external_modules import *
from shared.utils.tests.fixtures.models import *


def inject_fixture(mock_name, method):
    globals()[f"{mock_name}"] = binance_client_mock_factory(method, 'mock', 'futures')
    globals()[f"{mock_name}_spy"] = binance_client_mock_factory(method, 'spy', 'futures')


METHODS = [
    ("init_session", "_init_session"),
    ("ping", "ping"),
    ("futures_change_leverage", "futures_change_leverage"),
    ("futures_create_order", "futures_create_order"),
    ("get_symbol_ticker", "get_symbol_ticker")
]


for method in METHODS:
    inject_fixture(*method)


class TestBinanceFuturesTrader:

    symbol = "BTCUSDT"

    @pytest.mark.parametrize(
        "parameters,symbols,times_called,expected_value",
        [
            pytest.param(
                {"symbol": "BTCUSDT", "equity": 100},
                {},
                (0, 0),
                {"return_value": True, "balance": 100},
                id="SymbolStarted-True",
            ),
            pytest.param(
                {"symbol": "BTCUSDT",  "equity": 100, "leverage": 10},
                {},
                (1, 0),
                {"return_value": True, "balance": 100},
                id="SymbolStarted-ChangeLeverage-True",
            ),
            pytest.param(
                {"symbol": "BNBUSDT", "equity": 100},
                {},
                (0, 0),
                {"return_value": False, "balance": 0},
                id="TradingAccountDoesntExist-False",
            ),
            pytest.param(
                {"symbol": "BTCUSDT", "equity": 100},
                {"BTCUSDT"},
                (0, 0),
                {"return_value": True, "balance": 0},
                id="SymbolIsAlreadyBeingTraded-True",
            ),
            pytest.param(
                {"symbol": "XRPBTC", "equity": 100},
                {},
                (0, 0),
                {"return_value": False, "balance": 0},
                id="SymbolDoesNotExist-False",
            ),
        ]
    )
    def test_start_symbol_trading(
        self,
        parameters,
        symbols,
        times_called,
        expected_value,
        create_symbol,
        create_exchange,
        ping,
        init_session,
        futures_change_leverage,
        futures_change_leverage_spy,
        futures_create_order,
        futures_create_order_spy,
        get_symbol_ticker
    ):
        binance_trader = BinanceFuturesTrader()
        binance_trader.symbols = symbols
        binance_trader.current_balance = {parameters["symbol"]: 0}
        binance_trader.initial_balance = {parameters["symbol"]: 0}

        return_value = binance_trader.start_symbol_trading(**parameters)

        assert return_value == expected_value["return_value"]

        assert futures_change_leverage_spy.call_count == times_called[0]
        assert futures_create_order_spy.call_count == times_called[1]

        assert binance_trader.current_balance[parameters["symbol"]] == expected_value["balance"]
        assert binance_trader.initial_balance[parameters["symbol"]] == expected_value["balance"]

    @pytest.mark.parametrize(
        "symbol,symbols,position,units,times_called,expected_value",
        [
            pytest.param(
                "BTCUSDT",
                {"BTCUSDT": {}},
                1,
                0.1,
                1,
                True,
                id="SymbolExists-PositiveUnits-True",
            ),
            pytest.param(
                "BTCUSDT",
                {"BTCUSDT": {}},
                -1,
                -0.1,
                1,
                True,
                id="SymbolExists-NegativeUnits-True",
            ),
            pytest.param(
                "BTCUSDT",
                {},
                0,
                0.1,
                0,
                False,
                id="SymbolDoesNotExist-False",
            ),
            pytest.param(
                "BTCUSDT",
                {"BTCUSDT": {}},
                0,
                0,
                0,
                True,
                id="NoUnits-False",
            ),
        ]
    )
    def test_stop_symbol_trading(
        self,
        symbol,
        symbols,
        position,
        units,
        times_called,
        expected_value,
        create_symbol,
        create_exchange,
        create_orders,
        ping,
        init_session,
        futures_change_leverage,
        futures_create_order,
        futures_create_order_spy,
        get_symbol_ticker
    ):
        binance_trader = BinanceFuturesTrader()
        binance_trader.symbols = symbols

        binance_trader._set_position(symbol, position, pipeline_id=1)
        binance_trader.units[symbol] = units
        binance_trader.initial_balance[symbol] = 100
        binance_trader.current_balance[symbol] = 100

        return_value = binance_trader.stop_symbol_trading(symbol, pipeline_id=1)

        assert return_value == expected_value
        assert binance_trader.positions[symbol] == 0
        assert futures_create_order_spy.call_count == times_called

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
        create_pipeline,
        create_position,
        futures_change_leverage,
        futures_create_order,
        futures_create_order_spy,
        get_symbol_ticker
    ):
        ###########################################################################################
        #                                       SETUP                                             #
        ###########################################################################################

        print(f"initial_position: {initial_position}, signal: {signal}")

        pipeline_id = 1

        binance_trader = BinanceFuturesTrader()
        binance_trader.start_symbol_trading(self.symbol, 1000)
        binance_trader.trade(self.symbol, initial_position, amount="all", pipeline_id=pipeline_id)

        ###########################################################################################
        #                                       TEST                                              #
        ###########################################################################################

        binance_trader.trade(self.symbol, signal, amount="all", pipeline_id=pipeline_id)

        assert binance_trader._get_position(self.symbol) == signal

        number_orders = abs(initial_position - signal)

        assert futures_create_order_spy.call_count == number_orders + abs(initial_position)

        if number_orders > 0:
            order = Orders.objects.last()
            assert order.pipeline_id == pipeline_id

            positions = Position.objects.all()

            assert len(positions) == 1
            assert positions[0].position == signal
            assert positions[0].open if signal != 0 else not positions[0].open

        if initial_position == signal:
            assert Trade.objects.all().count() == abs(initial_position)
        else:
            trades = Trade.objects.all()

            assert len(trades) == max(number_orders, 1)
            assert trades[0].amount == float(futures_order_creation["executedQty"])
            assert trades[0].open_price == float(futures_order_creation["price"])

    def test_all(
        self,
        ping,
        init_session,
        create_symbol,
        create_exchange,
        create_pipeline,
        create_orders,
        futures_change_leverage,
        futures_change_leverage_spy,
        futures_create_order,
        futures_create_order_spy,
        get_symbol_ticker
    ):

        binance_trader = BinanceFuturesTrader()

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
