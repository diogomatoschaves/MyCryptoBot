import os

import pytest

from execution.service import create_app


TEST_APP_NAME = 'test_app'


@pytest.fixture()
def mock_client_env_vars(mocker):
    mocker.patch.dict(os.environ, {"APP_NAME": TEST_APP_NAME})


@pytest.fixture
def app(mock_client_env_vars):
    app = create_app(testing=True)
    return app


@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        yield client
