from model.service.helpers.responses import Responses
from model.tests.setup.fixtures.app import client, app, mock_client_env_vars
from model.tests.setup.fixtures.internal_modules import *
from model.tests.setup.fixtures.external_modules import mock_boto3_client
from model.tests.setup.test_data.sample_data import STRATEGIES
from model.tests.setup.fixtures.external_modules import *
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.fixtures.external_modules import mock_jwt_required


@pytest.fixture
def app_client(client, mock_jwt_required):
    return client


class TestModelService:
    def test_index_route(self, app_client):

        res = app_client.get("/")

        assert res.data.decode(res.charset) == "It's up!"

    @pytest.mark.parametrize(
        "route,method",
        [
            pytest.param(
                "generate_signal",
                "get",
                id="generate_signal_get",
            ),
            pytest.param(
                "generate_signal",
                "put",
                id="generate_signal_put",
            ),
            pytest.param(
                "generate_signal",
                "delete",
                id="generate_signal_delete",
            ),
            pytest.param(
                "check_job/123",
                "put",
                id="check_job_put",
            ),
            pytest.param(
                "check_job/123",
                "post",
                id="check_job_post",
            ),
            pytest.param(
                "check_job/123",
                "delete",
                id="strategies_delete",
            ),
            pytest.param(
                "strategies",
                "put",
                id="strategies_put",
            ),
            pytest.param(
                "strategies",
                "post",
                id="strategies_post",
            ),
            pytest.param(
                "strategies",
                "delete",
                id="strategies_delete",
            ),
        ],
    )
    def test_routes_disallowed_methods(self, route, method, app_client):
        """
        GIVEN a method for a certain route
        WHEN the method is invalid
        THEN the status code of the response will be 405

        equivalent to eg:

        res = client.get('/start_bot')

        """

        res = getattr(app_client, method)(route)

        print(res.data)

        assert res.status_code == 405

    @pytest.mark.parametrize(
        "return_value,expected_value",
        [
            pytest.param(
                mock_rq_job(is_finished=True, result=True),
                Responses.FINISHED(True),
                id="IS_FINISHED",
            ),
            pytest.param(
                mock_rq_job(is_finished=False, is_queued=True),
                Responses.IN_QUEUE,
                id="IS_QUEUED",
            ),
            pytest.param(
                mock_rq_job(is_finished=False, is_queued=False, is_started=True),
                Responses.WAITING,
                id="IS_STARTED",
            ),
            pytest.param(
                mock_rq_job(
                    is_finished=False, is_queued=False, is_started=False, is_failed=True
                ),
                Responses.FAILED,
                id="IS_FAILED",
            ),
        ],
    )
    def test_check_job_status(
        self, return_value, expected_value, app_client, mocked_rq_job
    ):

        mocked_rq_job.return_value = return_value

        res = app_client.get("/check_job/123")

        assert res.json == expected_value

    def test_check_job_status_no_such_job_error(self, app_client, mocked_rq_job):

        mocked_rq_job.side_effect = lambda job_id, connection: mock_rq_job(
            raise_error=True
        )

        res = app_client.get("/check_job/123")

        assert res.json == Responses.JOB_NOT_FOUND

    @pytest.mark.parametrize(
        "params,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 1
                },
                Responses.SIGNAL_GENERATION_INPROGRESS("abcde"),
                id="SIGNAL_GENERATION_INPROGRESS",
            ),
            pytest.param(
                {},
                Responses.NO_SUCH_PIPELINE('Pipeline None was not found.'),
                id="NO_SUCH_PIPELINE",
            ),
        ],
    )
    def test_generate_signal(
        self,
        params,
        expected_value,
        app_client,
        mock_settings_env_vars,
        mocked_rq_enqueue_call,
        mock_redis_connection,
        create_exchange,
        create_pipeline
    ):
        res = app_client.post("/generate_signal", json=params)

        assert res.json == expected_value

    @pytest.mark.slow
    def test_get_strategies(
        self,
        app_client,
        mock_settings_env_vars,
        mocked_rq_enqueue_call,
        mock_redis_connection,
        mock_compile_strategies,
        create_exchange,
        create_pipeline
    ):
        res = app_client.get("/strategies")

        print(res.json)

        assert res.json == STRATEGIES
