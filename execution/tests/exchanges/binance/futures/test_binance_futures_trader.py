import os

import django
import pytest

from execution.tests.setup.test_data.binance_api_responses import margin_order_creation

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from execution.service.helpers.exceptions import SymbolNotBeingTraded, SymbolAlreadyTraded, NegativeEquity, \
    InsufficientBalance
    from execution.exchanges.binance.futures import BinanceFuturesTrader
    from execution.tests.setup.fixtures.external_modules import *

from shared.utils.exceptions import SymbolInvalid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

from shared.utils.tests.fixtures.models import *


def inject_fixture(mock_name, method):
    globals()[f"{mock_name}"] = binance_client_mock_factory(method, 'mock')
    globals()[f"{mock_name}_spy"] = binance_client_mock_factory(method, 'spy')


METHODS = [
    ("init_session", "_init_session"),
    ("ping", "ping"),
    ("futures_symbol_ticker", "futures_symbol_ticker"),
    ("futures_change_leverage", "futures_change_leverage"),
    ("futures_create_order", "futures_create_order"),
    ("futures_account_balance", "futures_account_balance"),
]


for method in METHODS:
    inject_fixture(*method)


@pytest.fixture
def test_mock_setup(
    mocker,
    create_exchange,
    create_symbol,
    create_pipeline,
    create_pipeline_with_balance,
    create_pipeline_with_balance_2,
    ping,
    init_session,
    futures_symbol_ticker,
    futures_change_leverage,
    futures_create_order,
    futures_account_balance,
):
    return


class TestBinanceFuturesTrader:

    symbol = "BTCUSDT"

    @pytest.mark.parametrize(
        "parameters,balance_units,,times_called",
        [
            pytest.param(
                {
                    "pipeline_id": 4,
                    "initial_position": 0
                },
                (2000, -0.05),
                (1, 1, 0),
                id="SymbolStarted",
            ),
            pytest.param(
                {
                    "pipeline_id": 4,
                    "initial_position": 0
                },
                (2000, -0.05),
                (1, 1, 0),
                id="SymbolStarted-ChangeLeverage",
            ),
            pytest.param(
                {
                    "initial_position": 1,
                    "pipeline_id": 4
                },
                (2000, -0.05),
                (1, 1, 0),
                id="SymbolStarted-WithInitialPositionLONG",
            ),
            pytest.param(
                {
                    "initial_position": -1,
                    "pipeline_id": 4
                },
                (2000, -0.05),
                (1, 1, 0),
                id="SymbolStarted-WithInitialPositionSHORT",
            ),
            pytest.param(
                {
                    "initial_position": 1,
                    "pipeline_id": 11
                },
                (1000, 0),
                (1, 1, 0),
                id="SymbolStarted-WithInitialPositionLONG-not_enough_equity",
            ),
            pytest.param(
                {
                    "initial_position": -1,
                    "pipeline_id": 11
                },
                (1000, 0),
                (1, 1, 0),
                id="SymbolStarted-WithInitialPositionSHORT-not_enough_equity",
            ),
        ]
    )
    def test_start_symbol_trading(
        self,
        parameters,
        balance_units,
        times_called,
        test_mock_setup,
        create_paper_trading_pipeline,
        futures_change_leverage_spy,
        futures_create_order_spy,
    ):
        pipeline = Pipeline.objects.get(id=parameters["pipeline_id"])

        symbol = pipeline.symbol.name

        binance_trader = self.start_symbol_trading(parameters, symbol, {})

        assert futures_change_leverage_spy.call_count == times_called[0]
        assert futures_create_order_spy.call_count == times_called[2]

        assert binance_trader.units[symbol] == balance_units[1]
        assert binance_trader.current_balance[symbol] == balance_units[0]
        assert binance_trader.initial_balance[symbol] == pipeline.current_equity * pipeline.leverage
        assert binance_trader.position[symbol] == parameters["initial_position"]

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "parameters,symbols,position,units,times_called",
        [
            pytest.param(
                {"pipeline_id": 1, "symbol": "BTCUSDT"},
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
                {"pipeline_id": 1, "symbol": "BTCUSDT"},
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
            pytest.param(
                {"pipeline_id": 1, "symbol": "BTCUSDT"},
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
                id="SymbolExists-NoUnits-True",
            ),
            pytest.param(
                {"pipeline_id": 1, "symbol": "BTCUSDT"},
                {
                    "BTCUSDT": {
                        "price_precision": 2,
                        "quantity_precision": 3,
                        "baseAsset": "BTC",
                        "quoteAsset": "USDT"
                    }
                },
                0,
                None,
                0,
                id="SymbolExists-NullUnits-True",
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
        symbol = self.symbol

        binance_trader = self.stop_symbol_trading(
            parameters,
            symbols,
            position,
            units,
        )

        assert binance_trader.position[symbol] == 0
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
        binance_trader.initial_balance[self.symbol] = initial_balance
        binance_trader.current_balance[self.symbol] = initial_balance

        binance_trader.start_symbol_trading(pipeline_id, leverage=pipeline.leverage)
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

        if initial_position == signal:
            assert Trade.objects.all().count() == abs(initial_position)
        else:
            trades = Trade.objects.all()

            assert len(trades) == max(number_orders, 1)
            assert trades[0].amount == float(futures_order_creation["executedQty"])
            assert trades[0].open_price == float(futures_order_creation["price"])

    @pytest.mark.parametrize(
        "signal,side_effect,pipeline_id,initial_position",
        [
            pytest.param(
                1,
                [1000, 1000, None],
                12,
                0,
                id="Long-1",
            ),
            pytest.param(
                -1,
                [1000, 1000, None],
                12,
                0,
                id="Short-1",
            ),
            pytest.param(
                1,
                [1000, 1050, None],
                12,
                0,
                id="Long-2",
            ),
            pytest.param(
                -1,
                [1000, 1050, None],
                12,
                0,
                id="Short-2",
            ),
            pytest.param(
                1,
                [1000, 1300, None],
                12,
                0,
                id="Long-3",
            ),
            pytest.param(
                -1,
                [1000, 1100, None],
                12,
                0,
                id="Short-3",
            ),
            pytest.param(
                1,
                [1000, 1000, 990],
                4,
                -1,
                id="Start at Short",
            ),
        ]
    )
    def test_current_equity_updated(
        self,
        signal,
        side_effect,
        pipeline_id,
        initial_position,
        test_mock_setup,
        create_pipeline_with_balance_4,
        create_neutral_position,
        mocked_futures_create_order
    ):
        mocked_futures_create_order.side_effect = [
            {
                **futures_order_creation,
                "side": "BUY" if signal == 1 else "SELL",
                "orderId": randint(0, 1E9),
                "cumQuote": side_effect[0]
            },
            {
                **futures_order_creation,
                "orderId": randint(0, 1E9),
                "cumQuote": side_effect[1]
            },
            {
                **futures_order_creation,
                "orderId": randint(0, 1E9),
                "cumQuote": side_effect[2]
            }
        ]

        pipeline = Pipeline.objects.get(id=pipeline_id)

        symbol = pipeline.symbol.name

        parameters = dict(
            pipeline_id=pipeline.id,
            initial_position=initial_position
        )

        binance_trader = self.start_symbol_trading(parameters, symbol, {})

        initial_equity = binance_trader.current_equity[symbol]
        pnl = side_effect[1] - side_effect[0] if side_effect[2] is None else side_effect[2] - side_effect[0]

        binance_trader.trade(self.symbol, signal, amount="all", pipeline_id=pipeline.id)

        assert binance_trader.current_equity[symbol] == initial_equity

        binance_trader.trade(self.symbol, 0, amount="all", pipeline_id=pipeline.id)

        assert binance_trader.current_equity[symbol] == initial_equity + pnl * signal
        assert binance_trader.current_balance[symbol] == binance_trader.current_equity[symbol] * pipeline.leverage

    def test_all(
        self,
        create_pipeline,
        create_orders,
        test_mock_setup,
    ):
        pipeline = Pipeline.objects.get(id=1)

        parameters = dict(
            pipeline_id=pipeline.id,
            leverage=pipeline.leverage
        )

        binance_trader = self.start_symbol_trading(parameters, self.symbol, {})

        binance_trader.trade(self.symbol, 1, amount="all", pipeline_id=1)

        binance_trader.stop_symbol_trading(1, self.symbol)

        positions = Position.objects.all()

        assert len(positions) == 1
        assert positions[0].position == 0

        trades = Trade.objects.all()

        assert len(trades) == 1
        assert all(trade.amount == float(margin_order_creation["executedQty"]) for trade in trades)
        assert all(trade.open_price == float(margin_order_creation["price"]) for trade in trades)

    @pytest.mark.parametrize(
        "parameters,symbols,times_called,expected_exception",
        [
            pytest.param(
                {"pipeline_id": 1, "leverage": 1},
                {"BTCUSDT"},
                (0, 0, 0),
                SymbolAlreadyTraded,
                id="SymbolIsAlreadyBeingTraded",
            ),
            pytest.param(
                {"pipeline_id": 13, "leverage": 1},
                {},
                (1, 0, 1),
                InsufficientBalance,
                id="InsufficientBalance",
            ),
        ]
    )
    def test_exception_start_symbol_trading(
        self,
        parameters,
        symbols,
        times_called,
        expected_exception,
        test_mock_setup,
        create_pipeline_with_current_equity,
        futures_change_leverage_spy,
        futures_account_balance_spy,
        futures_create_order_spy,
    ):
        with pytest.raises(Exception) as exception:
            self.start_symbol_trading(parameters, self.symbol, symbols)

        assert exception.type == expected_exception
        assert futures_change_leverage_spy.call_count == times_called[0]
        assert futures_create_order_spy.call_count == times_called[1]
        assert futures_account_balance_spy.call_count == times_called[2]

    @pytest.mark.parametrize(
        "parameters,symbols,position,units,times_called,expected_value",
        [
            pytest.param(
                {"pipeline_id": 1, "symbol": "BTCUSDT"},
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
            self.stop_symbol_trading(
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
        mocked_futures_create_order,
        create_orders,
        futures_create_order_spy,
    ):
        mocked_futures_create_order.side_effect = side_effect

        with pytest.raises(Exception) as exception:

            pipeline_id = 6

            parameters = dict(
                pipeline_id=pipeline_id,
                leverage=1
            )

            binance_trader = self.start_symbol_trading(parameters, self.symbol, {})

            binance_trader.trade(self.symbol, positions[0], amount="all", pipeline_id=pipeline_id)
            binance_trader.trade(self.symbol, positions[1], amount="all", pipeline_id=pipeline_id)
            binance_trader.trade(self.symbol, positions[0], amount="all", pipeline_id=pipeline_id)

        assert exception.type == expected_value
        assert futures_create_order_spy.call_count == times_called

    @staticmethod
    def start_symbol_trading(parameters, symbol, symbols):
        binance_trader = BinanceFuturesTrader()
        binance_trader.symbols = symbols
        binance_trader.current_balance = {symbol: 0}
        binance_trader.initial_balance = {symbol: 0}
        binance_trader.current_equity = {symbol: 0}

        binance_trader.start_symbol_trading(**parameters)

        return binance_trader

    @staticmethod
    def stop_symbol_trading(parameters, symbols, position, units):

        symbol = parameters["symbol"]

        binance_trader = BinanceFuturesTrader()
        binance_trader.symbols = symbols

        binance_trader._set_position(symbol, position, pipeline_id=1)
        if units is not None:
            binance_trader.units[symbol] = units

        binance_trader.initial_balance[symbol] = 1000
        binance_trader.current_balance[symbol] = 1000
        binance_trader.current_equity[symbol] = 100

        binance_trader.start_date[symbol] = datetime.datetime.now(tz=pytz.utc)

        binance_trader.stop_symbol_trading(**parameters)

        return binance_trader
