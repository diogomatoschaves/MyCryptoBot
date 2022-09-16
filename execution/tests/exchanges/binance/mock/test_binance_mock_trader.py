from execution.exchanges.binance.margin.mock import BinanceMockTrader
from execution.tests.setup.fixtures.external_modules import binance_mock_trader_spy_factory
from shared.utils.tests.fixtures.models import *


def inject_fixture(mock_name):
    globals()[f"{mock_name}_spy"] = binance_mock_trader_spy_factory(method)


METHODS = [
    "get_isolated_margin_account",
    "create_margin_loan",
    "get_trade_fee",
    "get_max_margin_loan",
    "create_margin_order",
    "repay_margin_loan",
]

for method in METHODS:
    inject_fixture(method)


class TestBinanceMockTrader:

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
        create_structured_data,
        get_isolated_margin_account_spy,
        create_margin_loan_spy,
        get_trade_fee_spy,
        get_max_margin_loan_spy,
        create_margin_order_spy
    ):
        binance_trader = BinanceMockTrader()
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
        create_structured_data,
        create_margin_order_spy,
        repay_margin_loan_spy
    ):
        binance_trader = BinanceMockTrader()
        binance_trader.symbols = symbols

        binance_trader._set_position(self.symbol, 1, pipeline_id=1)
        binance_trader.units = units
        binance_trader.initial_balance = 100
        binance_trader.max_borrow_amount = {
            self.symbol: {
                "BTC": "60", "USDT": "1000"
            }
        }

        binance_trader.stop_symbol_trading(self.symbol, pipeline_id=1)

        assert repay_margin_loan_spy.call_count == times_called[0]
        assert create_margin_order_spy.call_count == times_called[1]

    @pytest.mark.parametrize("initial_position", [-1, 0, 1])
    @pytest.mark.parametrize("signal", [-1, 0, 1])
    def test_trade(
        self,
        initial_position,
        signal,
        create_symbol,
        create_exchange,
        create_structured_data,
        create_margin_order_spy
    ):
        binance_trader = BinanceMockTrader()
        binance_trader.start_symbol_trading(self.symbol)
        binance_trader.symbols = {
            self.symbol: {
                "quote": "USDT", "base": "BTC"
            }
        }

        binance_trader._set_position(self.symbol, initial_position)

        binance_trader.trade(self.symbol, signal, amount="all")

        assert binance_trader._get_position(self.symbol) == signal

        assert Orders.objects.all().count() == abs(initial_position - signal) + 1

        assert create_margin_order_spy.call_count == abs(initial_position - signal) + 1
