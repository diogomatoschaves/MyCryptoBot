import os

import django
import pytest

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from execution.service.helpers.exceptions import SymbolNotBeingTraded, NoUnits, SymbolAlreadyTraded, NegativeEquity
    from execution.exchanges.binance.futures import BinanceFuturesTrader
    from execution.tests.setup.fixtures.external_modules import *
    from execution.tests.setup.fixtures.internal_modules import mock_futures_symbol_ticker

from shared.utils.exceptions import SymbolInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from shared.utils.tests.fixtures.models import *


def inject_fixture(mock_name, method, extra_info):
    globals()[f"{mock_name}"] = binance_client_mock_factory(method, 'mock', 'futures', extra_info)
    globals()[f"{mock_name}_spy"] = binance_client_mock_factory(method, 'spy', 'futures')


METHODS = [
    ("init_session", "_init_session", None),
    ("ping", "ping", None),
    ("futures_change_leverage", "futures_change_leverage", None),
    ("futures_create_order", "futures_create_order", None),
    ("futures_exchange_info", "futures_exchange_info", None),
    ("get_symbol_ticker", "get_symbol_ticker", None)
]


for method in METHODS:
    inject_fixture(*method)


@pytest.fixture
def test_mock_setup(
    mocker,
    create_exchange,
    create_symbol,
    create_pipeline_with_balance,
    create_pipeline_with_balance_2,
    ping,
    init_session,
    futures_change_leverage,
    futures_create_order,
    futures_exchange_info,
    get_symbol_ticker,
    mock_futures_symbol_ticker
):
    return


class TestBinanceFuturesTrader:

    symbol = "BTCUSDT"

    @pytest.mark.parametrize(
        "parameters,symbols,times_called,balance,initial_position",
        [
            pytest.param(
                {"symbol": "BTCUSDT", "starting_equity": 100, "pipeline_id": 4},
                {},
                (0, 1, 0),
                100,
                0,
                id="SymbolStarted",
            ),
            pytest.param(
                {"symbol": "BTCUSDT",  "starting_equity": 100, "leverage": 10, "pipeline_id": 4},
                {},
                (1, 1, 0),
                100,
                0,
                id="SymbolStarted-ChangeLeverage",
            ),
            pytest.param(
                {"symbol": "BTCUSDT",  "starting_equity": 100, "initial_position": 1, "pipeline_id": 4},
                {},
                (0, 1, 0),
                100,
                1,
                id="SymbolStarted-WithInitialPositionLONG",
            ),
            pytest.param(
                {"symbol": "BTCUSDT",  "starting_equity": 100, "initial_position": -1, "pipeline_id": 4},
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
        futures_create_order_spy,
    ):
        binance_trader = self.start_symbol_trading(parameters, symbols)

        assert futures_change_leverage_spy.call_count == times_called[0]
        assert futures_create_order_spy.call_count == times_called[2]

        symbol = parameters["symbol"]

        assert binance_trader.units[symbol] == -2
        assert binance_trader.current_balance[symbol] == 2000
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
        create_neutral_position,
        futures_create_order_spy,
    ):
        ###########################################################################################
        #                                       SETUP                                             #
        ###########################################################################################

        print(f"initial_position: {initial_position}, signal: {signal}")

        pipeline_id = 5
        pipeline = Pipeline.objects.get(id=pipeline_id)
        initial_balance = pipeline.balance

        binance_trader = BinanceFuturesTrader()
        binance_trader.start_symbol_trading(self.symbol, initial_balance, pipeline_id=pipeline_id)
        binance_trader.trade(self.symbol, initial_position, amount="all", pipeline_id=pipeline_id)

        ###########################################################################################
        #                                       TEST                                              #
        ###########################################################################################

        binance_trader.trade(self.symbol, signal, amount="all", pipeline_id=pipeline_id)

        assert binance_trader._get_position(self.symbol) == signal

        factor = (signal - 1) * -1

        assert binance_trader.units[self.symbol] == float(futures_order_creation["origQty"]) * signal
        assert binance_trader.initial_balance[self.symbol] == initial_balance
        assert binance_trader.current_balance[self.symbol] == initial_balance * factor

        number_orders = abs(initial_position - signal)

        assert futures_create_order_spy.call_count == number_orders + abs(initial_position)

        if number_orders > 0:
            order = Orders.objects.last()
            assert order.pipeline_id == pipeline_id

            positions = Position.objects.all()

            assert len(positions) == 2

            position = Position.objects.get(pipeline__id=pipeline_id)

            assert position.position == signal
            assert position.open if signal != 0 else not position.open

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
        test_mock_setup,
    ):
        starting_equity = 1000

        binance_trader = BinanceFuturesTrader()

        binance_trader.start_symbol_trading(self.symbol, starting_equity, pipeline_id=1)

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
                {"symbol": "BTCUSDT", "starting_equity": 100},
                {"BTCUSDT"},
                (0, 0),
                0,
                SymbolAlreadyTraded,
                id="SymbolIsAlreadyBeingTraded",
            ),
            pytest.param(
                {"symbol": "XRPBTC", "starting_equity": 100},
                {},
                (0, 0),
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
        futures_create_order_spy,
    ):
        with pytest.raises(Exception) as exception:
            binance_trader = self.start_symbol_trading(parameters, symbols)

        assert exception.type == expected_exception
        assert futures_change_leverage_spy.call_count == times_called[0]
        assert futures_create_order_spy.call_count == times_called[1]

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
        assert futures_create_order_spy.call_count == times_called

    @pytest.mark.parametrize(
        "side_effect,positions,times_called,expected_value",
        [
            pytest.param(
                [
                    {
                        **futures_order_creation,
                        "side": -1,
                        "orderId": randint(0, 1E9),
                        "cumQuote": 120,
                        "executedQty": "0.005"
                    },
                    {
                        **futures_order_creation,
                        "side": 1,
                        "orderId": randint(0, 1E9),
                        "cumQuote": 10,
                        "executedQty": "0.005"
                    },
                ],
                (1, -1),
                2,
                NegativeEquity,
                id="NegativeEquity-(1, -1)",
            ),
            pytest.param(
                [
                    {
                        **futures_order_creation,
                        "side": -1,
                        "orderId": randint(0, 1E9),
                        "cumQuote": 50,
                        "executedQty": "0.005"
                    },
                    {
                        **futures_order_creation,
                        "side": 1,
                        "orderId": randint(0, 1E9),
                        "cumQuote": 200,
                        "executedQty": "0.005"
                    },
                ],
                (-1, 1),
                2,
                NegativeEquity,
                id="NegativeEquity-(-1, 1)",
            ),
        ]
    )
    def test_exception_trade(
        self,
        side_effect,
        positions,
        times_called,
        expected_value,
        test_mock_setup,
        create_pipeline_with_balance_3,
        futures_create_order_negative_equity,
        create_orders,
        futures_create_order_spy,
    ):

        futures_create_order_negative_equity.side_effect = side_effect

        with pytest.raises(Exception) as exception:

            pipeline_id = 6
            initial_balance = 100

            binance_trader = BinanceFuturesTrader()
            binance_trader.start_symbol_trading(self.symbol, initial_balance, pipeline_id=pipeline_id)
            binance_trader.trade(self.symbol, positions[0], amount="all", pipeline_id=pipeline_id)

            binance_trader.trade(self.symbol, positions[1], amount="all", pipeline_id=pipeline_id)
            binance_trader.trade(self.symbol, positions[0], amount="all", pipeline_id=pipeline_id)

        assert exception.type == expected_value
        assert futures_create_order_spy.call_count == times_called

    @staticmethod
    def stop_symbol_trading(parameters, symbols, position, units):
        binance_trader = BinanceFuturesTrader()
        binance_trader.symbols = symbols

        symbol = parameters["symbol"]

        binance_trader._set_position(symbol, position, pipeline_id=1)
        binance_trader.units[symbol] = units
        binance_trader.initial_balance[symbol] = 1000
        binance_trader.current_balance[symbol] = 1000

        binance_trader.stop_symbol_trading(**parameters)

        return binance_trader
