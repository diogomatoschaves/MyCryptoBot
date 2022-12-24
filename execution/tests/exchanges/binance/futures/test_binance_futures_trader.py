import os

import django
import pytest

from execution.service.helpers.exceptions import SymbolNotBeingTraded, NoUnits, SymbolAlreadyTraded
from shared.utils.exceptions import SymbolInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

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
    ("futures_exchange_info", "futures_exchange_info"),
    ("get_symbol_ticker", "get_symbol_ticker")
]


for method in METHODS:
    inject_fixture(*method)


@pytest.fixture
def test_mock_setup(
    mocker,
    create_exchange,
    create_symbol,
    ping,
    init_session,
    futures_change_leverage,
    futures_create_order,
    futures_exchange_info,
    get_symbol_ticker
):
    return


class TestBinanceFuturesTrader:

    symbol = "BTCUSDT"

    @pytest.mark.parametrize(
        "parameters,symbols,times_called,balance,initial_position",
        [
            pytest.param(
                {"symbol": "BTCUSDT", "equity": 100},
                {},
                (0, 1, 0),
                100,
                0,
                id="SymbolStarted",
            ),
            pytest.param(
                {"symbol": "BTCUSDT",  "equity": 100, "leverage": 10},
                {},
                (1, 1, 0),
                100,
                0,
                id="SymbolStarted-ChangeLeverage",
            ),
            pytest.param(
                {"symbol": "BTCUSDT",  "equity": 100, "initial_position": 1},
                {},
                (0, 1, 0),
                100,
                1,
                id="SymbolStarted-WithInitialPositionLONG",
            ),
            pytest.param(
                {"symbol": "BTCUSDT",  "equity": 100, "initial_position": -1},
                {},
                (0, 1, 0),
                100,
                -1,
                id="SymbolStarted-WithInitialPositionSHORT",
            ),
        ]
    )
    def test_start_symbol_trading(
        self,
        parameters,
        symbols,
        times_called,
        balance,
        initial_position,
        test_mock_setup,
        futures_change_leverage_spy,
        futures_exchange_info_spy,
        futures_create_order_spy,
    ):
        binance_trader = self.start_symbol_trading(parameters, symbols)

        assert futures_change_leverage_spy.call_count == times_called[0]
        assert futures_exchange_info_spy.call_count == times_called[1]
        assert futures_create_order_spy.call_count == times_called[2]

        symbol = parameters["symbol"]

        assert binance_trader.units[symbol] == initial_position * 0.005
        assert binance_trader.current_balance[symbol] == (initial_position - 1) * -1 * balance
        assert binance_trader.initial_balance[symbol] == balance
        assert binance_trader.positions[symbol] == initial_position

    @pytest.mark.parametrize(
        "parameters,symbols,position,units,times_called",
        [
            pytest.param(
                {"symbol": "BTCUSDT", "pipeline_id": 1},
                {
                    "BTCUSDT": {
                        "price_precision": 2,
                        "quantity_precision": 3,
                        "baseAsset": "BTC",
                        "quoteAsset": "USDT"
                    }
                },
                1,
                0.1,
                1,
                id="SymbolExists-PositiveUnits-True",
            ),
            pytest.param(
                {"symbol": "BTCUSDT", "pipeline_id": 1},
                {
                    "BTCUSDT": {
                        "price_precision": 2,
                        "quantity_precision": 3,
                        "baseAsset": "BTC",
                        "quoteAsset": "USDT"
                    }
                },
                -1,
                -0.1,
                1,
                id="SymbolExists-NegativeUnits-True",
            ),
        ]
    )
    def test_stop_symbol_trading(
        self,
        parameters,
        symbols,
        position,
        units,
        times_called,
        test_mock_setup,
        create_orders,
        futures_create_order_spy,
    ):

        binance_trader = self.stop_symbol_trading(
            parameters,
            symbols,
            position,
            units,
        )

        symbol = parameters["symbol"]

        assert binance_trader.positions[symbol] == 0
        assert futures_create_order_spy.call_count == times_called

    @pytest.mark.parametrize("signal", [-1, 0, 1])
    @pytest.mark.parametrize("initial_position", [-1, 0, 1])
    def test_trade(
        self,
        initial_position,
        signal,
        test_mock_setup,
        create_pipeline,
        create_position,
        futures_create_order_spy,
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
        create_pipeline,
        create_orders,
        test_mock_setup
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

    @pytest.mark.parametrize(
        "parameters,symbols,times_called,balance,expected_exception",
        [
            pytest.param(
                {"symbol": "BTCUSDT", "equity": 100},
                {"BTCUSDT"},
                (0, 0, 0),
                0,
                SymbolAlreadyTraded,
                id="SymbolIsAlreadyBeingTraded",
            ),
            pytest.param(
                {"symbol": "XRPBTC", "equity": 100},
                {},
                (0, 1, 0),
                0,
                SymbolInvalid,
                id="SymbolInvalid",
            ),
        ]
    )
    def test_exception_start_symbol_trading(
        self,
        parameters,
        symbols,
        times_called,
        balance,
        expected_exception,
        test_mock_setup,
        futures_change_leverage_spy,
        futures_exchange_info_spy,
        futures_create_order_spy,
    ):
        with pytest.raises(Exception) as exception:
            binance_trader = self.start_symbol_trading(parameters, symbols)

            assert exception.type == expected_exception
            assert futures_change_leverage_spy.call_count == times_called[0]
            assert futures_exchange_info_spy.call_count == times_called[1]
            assert futures_create_order_spy.call_count == times_called[2]

            assert binance_trader.current_balance[parameters["symbol"]] == balance
            assert binance_trader.initial_balance[parameters["symbol"]] == balance

    @staticmethod
    def start_symbol_trading(parameters, symbols):
        binance_trader = BinanceFuturesTrader()
        binance_trader.symbols = symbols
        binance_trader.current_balance = {parameters["symbol"]: 0}
        binance_trader.initial_balance = {parameters["symbol"]: 0}

        binance_trader.start_symbol_trading(**parameters)

        return binance_trader

    @pytest.mark.parametrize(
        "parameters,symbols,position,units,times_called,expected_value",
        [
            pytest.param(
                {"symbol": "BTCUSDT", "pipeline_id": 1},
                {},
                0,
                0.1,
                0,
                SymbolNotBeingTraded,
                id="SymbolNotBeingTraded",
            ),
            pytest.param(
                {"symbol": "BTCUSDT", "pipeline_id": 1},
                {
                    "BTCUSDT": {
                        "price_precision": 2,
                        "quantity_precision": 3,
                        "baseAsset": "BTC",
                        "quoteAsset": "USDT"
                    }
                },
                0,
                0,
                0,
                NoUnits,
                id="NoUnits",
            )
        ]
    )
    def test_exception_stop_symbol_trading(
        self,
        parameters,
        symbols,
        position,
        units,
        times_called,
        expected_value,
        test_mock_setup,
        create_orders,
        futures_create_order_spy,
    ):
        with pytest.raises(Exception) as exception:
            bt = self.stop_symbol_trading(
                parameters,
                symbols,
                position,
                units,
            )

            assert exception.type == expected_value
            assert bt.positions[parameters["symbol"]] == 0
            assert futures_create_order_spy.call_count == times_called

    @staticmethod
    def stop_symbol_trading(parameters, symbols, position, units):
        binance_trader = BinanceFuturesTrader()
        binance_trader.symbols = symbols

        symbol = parameters["symbol"]

        binance_trader._set_position(symbol, position, pipeline_id=1)
        binance_trader.units[symbol] = units
        binance_trader.initial_balance[symbol] = 100
        binance_trader.current_balance[symbol] = 100

        return_value = binance_trader.stop_symbol_trading(**parameters)

        return binance_trader
