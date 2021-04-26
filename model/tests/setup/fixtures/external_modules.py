import pytest
from rq.exceptions import NoSuchJobError

import model


def mock_rq_job(*args, **kwargs):
    class MockJob:
        def __init__(self):
            for kwarg, value in kwargs.items():
                setattr(self, kwarg, value)

            if "raise_error" in kwargs:
                raise NoSuchJobError

    return MockJob()


@pytest.fixture
def mocked_rq_job(mocker):
    return mocker.patch("rq.job.Job.fetch")


def mock_enqueue_call(get_signal, params):
    class MockJob:
        def __init__(self):
            pass

        def get_id(self):
            return "abcde"

    return MockJob()


@pytest.fixture
def mocked_rq_enqueue_call(mocker):
    return mocker.patch.object(model.service.app.q, "enqueue_call", mock_enqueue_call)
