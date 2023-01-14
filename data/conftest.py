import pytest


class FakeBinanceClient:
    def __init__(self):
        pass

    def futures_exchange_info(self):
        print('this was called')
        return {"symbols": [{"symbol": "BTCUSDT"}]}


@pytest.fixture(autouse=True)
def mock_binance_client(mocker):
    return mocker.patch('data.service.blueprints.bots_api.binance_client', FakeBinanceClient())


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")
