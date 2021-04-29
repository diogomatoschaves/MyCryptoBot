import pytest

from execution.exchanges.binance import BinanceTrader
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


class TestBinanceTrader:

    symbol = "BTCUSDT"

    def test_start_symbol_trading(
        self,
        create_symbol,
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
        binance_trader = BinanceTrader()
        binance_trader.start_symbol_trading(self.symbol)

        get_trade_fee_spy.assert_called()
        get_isolated_margin_account_spy.assert_called()
        create_margin_order_spy.assert_called()

        assert get_trade_fee_spy.call_count == 1
        assert get_max_margin_loan_spy.call_count == 2
        assert create_margin_loan_spy.call_count == 1

    def test_stop_symbol_trading(
        self,
        create_symbol,
        ping,
        init_session,
        create_margin_order,
        create_margin_order_spy,
        repay_margin_loan,
        repay_margin_loan_spy
    ):
        binance_trader = BinanceTrader()
        binance_trader.symbols = {
            self.symbol: {
                "quote": "USDT", "base": "BTC"
            }
        }

        binance_trader._set_position(self.symbol, 1)
        binance_trader.units = 0.1
        binance_trader.initial_balance = 100
        binance_trader.max_borrow_amount = {
            self.symbol: {
                "BTC": "60", "USDT": "1000"
            }
        }

        binance_trader.stop_symbol_trading(self.symbol)

        assert repay_margin_loan_spy.call_count == 2
        assert create_margin_order_spy.call_count == 1

    @pytest.mark.parametrize("initial_position", [-1, 0, 1])
    @pytest.mark.parametrize("signal", [-1, 0, 1])
    def test_trade(
        self,
        initial_position,
        signal,
        ping,
        init_session,
        create_symbol,
        create_margin_order,
        create_margin_order_spy,
    ):
        binance_trader = BinanceTrader()
        binance_trader.symbols = {
            self.symbol: {
                "quote": "USDT", "base": "BTC"
            }
        }

        binance_trader._set_position(self.symbol, initial_position)

        binance_trader.trade(self.symbol, signal, amount="all")

        assert binance_trader._get_position(self.symbol) == signal

        assert create_margin_order_spy.call_count == abs(initial_position - signal)
