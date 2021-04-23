import time

import pytest
import requests

response = {"response": "Something", "success": True}


def mock_response(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.ok = True

        def json(self):
            return self.json_data

        @property
        def text(self):
            return response["response"]

    return MockResponse(response, 200)


@pytest.fixture
def mock_requests_post(mocker):
    return mocker.patch.object(requests, "post", mock_response)


@pytest.fixture
def requests_post_spy(mocker):
    return mocker.spy(requests, "post")


@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch.object(requests, "get", mock_response)


@pytest.fixture
def requests_get_spy(mocker):
    return mocker.spy(requests, "get")


@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch.object(time, "sleep", lambda seconds: None)
