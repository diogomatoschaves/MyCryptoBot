import pytest
from binance.client import Client


@pytest.fixture
def mock_binance_client_init(mocker):
    mocker.patch.object(Client, "_init_session", lambda self: None)


@pytest.fixture
def mock_binance_client_ping(mocker):
    mocker.patch.object(Client, "ping", lambda self: None)
