import os

import pytest


TEST_APP_NAME = 'test_app'


@pytest.fixture()
def mock_settings_env_vars(mocker):
    mocker.patch.dict(os.environ, {
        "APP_NAME": TEST_APP_NAME,
    })