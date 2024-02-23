import plotly
import pytest
from botocore.exceptions import ClientError, NoCredentialsError
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


class MockS3Client:
    def __init__(self, raise_client_error=False, raise_no_credentials_error=False):
        self.raise_client_error = raise_client_error
        self.raise_no_credentials_error = raise_no_credentials_error

    def list_objects(self, Bucket):
        if self.raise_client_error:
            raise ClientError({"Error": {}}, [])
        elif self.raise_no_credentials_error:
            raise NoCredentialsError
        else:
            return {'Contents': [{'Key': 'file1'}, {'Key': 'file2'}]}

    def upload_fileobj(self, file_obj, bucket, filename):
        return True

    def download_file(self, bucket, filename, filepath):

        return True


@pytest.fixture
def mock_boto3_client(mocker):
    return mocker.patch(
        "model.service.cloud_storage._cloud_storage.s3",
        MockS3Client()
    )


@pytest.fixture
def mock_boto3_client_raise_client_error(mocker):
    return mocker.patch(
        "model.service.cloud_storage._cloud_storage.s3",
        MockS3Client(raise_client_error=True)
    )


@pytest.fixture
def mock_boto3_client_raise_no_credentials_error(mocker):
    return mocker.patch(
        "model.service.cloud_storage._cloud_storage.s3",
        MockS3Client(raise_no_credentials_error=True)
    )
