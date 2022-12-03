import time

import pytest
import requests
from flask_jwt_extended import view_decorators

response = {"message": "Something", "success": True}


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
            return response["message"]

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


def mock_verify_jwt_in_request(
    optional: bool = False,
    fresh: bool = False,
    refresh: bool = False,
    locations = None,
    verify_type: bool = True,
):
    pass


@pytest.fixture
def mock_jwt_required(mocker):
    return mocker.patch.object(view_decorators, "verify_jwt_in_request", mock_verify_jwt_in_request)
