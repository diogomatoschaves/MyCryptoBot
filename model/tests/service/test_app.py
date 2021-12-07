from model.service.helpers.responses import Responses
from model.tests.setup.fixtures.app import *
from model.tests.setup.fixtures.internal_modules import mock_settings_env_vars
from model.tests.setup.fixtures.external_modules import *
from shared.utils.tests.fixtures.models import *


class TestModelService:
    def test_index_route(self, client):

        res = client.get("/")

        assert res.data.decode(res.charset) == "It's up!"

    @pytest.mark.parametrize(
        "route,method",
        [
            pytest.param(
                "generate_signal",
                "get",
                id="start_bot_get",
            ),
            pytest.param(
                "generate_signal",
                "put",
                id="start_bot_post",
            ),
            pytest.param(
                "generate_signal",
                "delete",
                id="start_bot_delete",
            ),
            pytest.param(
                "check_job/123",
                "put",
                id="start_bot_delete",
            ),
            pytest.param(
                "check_job/123",
                "post",
                id="start_bot_delete",
            ),
            pytest.param(
                "check_job/123",
                "delete",
                id="start_bot_delete",
            ),
        ],
    )
    def test_routes_disallowed_methods(self, route, method, client):
        """
        GIVEN a method for a certain route
        WHEN the method is invalid
        THEN the status code of the response will be 405

        equivalent to eg:

        res = client.get('/start_bot')

        """

        res = getattr(client, method)(route)

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
        self, return_value, expected_value, client, mocked_rq_job
    ):

        mocked_rq_job.return_value = return_value

        res = client.get("/check_job/123")

        assert res.json == expected_value

    def test_check_job_status_no_such_job_error(self, client, mocked_rq_job):

        mocked_rq_job.side_effect = lambda job_id, connection: mock_rq_job(
            raise_error=True
        )

        res = client.get("/check_job/123")

        assert res.json == Responses.JOB_NOT_FOUND

    @pytest.mark.parametrize(
        "params,nr_jobs,expected_value",
        [
            pytest.param(
                {
                    "pipeline_id": 1
                },
                1,
                Responses.SIGNAL_GENERATION_INPROGRESS("abcde"),
                id="SIGNAL_GENERATION_INPROGRESS",
            ),
            pytest.param(
                {},
                0,
                Responses.NO_SUCH_PIPELINE(None),
                id="NO_SUCH_PIPELINE",
            ),
        ],
    )
    def test_generate_signal(
        self,
        params,
        nr_jobs,
        expected_value,
        client,
        mock_settings_env_vars,
        mocked_rq_enqueue_call,
        create_exchange,
        create_pipeline
    ):
        res = client.post("/generate_signal", json=params)

        assert res.json == expected_value

        assert Jobs.objects.filter(job_id="abcde").count() == nr_jobs
