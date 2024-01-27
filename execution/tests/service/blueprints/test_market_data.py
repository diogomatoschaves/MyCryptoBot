import pytest

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from execution.service.helpers.responses import Responses
    from execution.tests.setup.fixtures.app import *
    from execution.tests.setup.fixtures.external_modules import *
    from execution.tests.setup.fixtures.internal_modules import *

from shared.utils.tests.fixtures.models import *
from shared.utils.tests.fixtures.external_modules import mock_jwt_required


def inject_fixture(mock_name, method):
    globals()[f"{mock_name}"] = binance_handler_market_data_factory(method)


METHODS = [
    ("init_session", "_init_session"),
    ("ping", "ping"),
    ("futures_symbol_ticker", "futures_symbol_ticker"),
    ("futures_account_balance", "futures_account_balance"),
    ("futures_position_information", "futures_position_information"),
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
    futures_symbol_ticker,
    futures_account_balance,
    futures_position_information
):
    return


class TestMarketData:

    @pytest.mark.parametrize(
        "route,method",
        [
            pytest.param(
                '/prices',
                'post',
                id="prices_post",
            ),
            pytest.param(
                '/prices',
                'put',
                id="prices_put",
            ),
            pytest.param(
                '/prices',
                'delete',
                id="prices_delete",
            ),
            pytest.param(
                '/futures_account_balance',
                'post',
                id="futures-account-balance_post",
            ),
            pytest.param(
                '/futures_account_balance',
                'put',
                id="futures-account-balance_put",
            ),
            pytest.param(
                '/futures_account_balance',
                'delete',
                id="futures-account-balance_delete",
            ),
            pytest.param(
                '/open-positions',
                'post',
                id="/open-positions_post",
            ),
            pytest.param(
                '/open-positions',
                'put',
                id="/open-positions_put",
            ),
            pytest.param(
                '/open-positions',
                'delete',
                id="/open-positions_delete",
            ),
        ],
    )
    def test_routes_disallowed_methods(self, route, method, client):

        res = getattr(client, method)(route)

        assert res.status_code == 405

    @pytest.mark.parametrize(
        "extra_url,response",
        [
            pytest.param(
                '',
                {},
                id="prices-no_symbol",
            ),
            pytest.param(
                '?symbol=BTCUSDT',
                {'symbol': 'BTCUSDT', 'price': 40000},
                id="prices-existent_symbol",
            ),
            pytest.param(
                '?symbol=BTC',
                {},
                id="prices-non_existent_symbol",
            ),
        ],
    )
    def test_get_prices_endpoint(
        self,
        extra_url,
        response,
        client,
        test_mock_setup
    ):
        res = client.get(f'/prices{extra_url}')

        assert res.json == response

    @pytest.mark.parametrize(
        "response",
        [
            pytest.param(
                {
                    "live": [
                        {
                            "accountAlias": "FzFzfWuXmYSguX",
                            "asset": "USDT",
                            "availableBalance": "10000",
                            "balance": "10000",
                            "crossUnPnl": "0.00000000",
                            "crossWalletBalance": "1952.45550004",
                            "marginAvailable": True,
                            "maxWithdrawAmount": "1952.45550004",
                            "updateTime": 1704326426077,
                        }
                    ],
                    "testnet": [
                        {
                            "accountAlias": "FzFzfWuXmYSguX",
                            "asset": "USDT",
                            "availableBalance": "10000",
                            "balance": "10000",
                            "crossUnPnl": "0.00000000",
                            "crossWalletBalance": "1952.45550004",
                            "marginAvailable": True,
                            "maxWithdrawAmount": "1952.45550004",
                            "updateTime": 1704326426077,
                        }
                    ],
                },
                id="futures_account_balance",
            ),
        ],
    )
    def test_futures_account_balance(
        self,
        response,
        client,
        test_mock_setup
    ):
        res = client.get(f'/futures_account_balance')

        print(res.json)

        assert res.json == response

    @pytest.mark.parametrize(
        "extra_url,response",
        [
            pytest.param(
                '',
                {'positions': {'live': None, 'testnet': None}, 'success': False},
                id="open_positions-no_symbol",
            ),
            pytest.param(
                '?symbol=BTCUSDT',
                {'positions': {'live': 0.0, 'testnet': 0.0}, 'success': True},
                id="open_positions-existent_symbol",
            ),
            pytest.param(
                '?symbol=BTC',
                {'positions': {'live': None, 'testnet': None}, 'success': False},
                id="open_positions-non_existent_symbol",
            ),
        ],
    )
    def test_open_positions(
        self,
        extra_url,
        response,
        client,
        test_mock_setup
    ):
        res = client.get(f'/open-positions{extra_url}')

        print(res.json)

        assert res.json == response
