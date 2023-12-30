import pytest
from flask import jsonify

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from data.tests.setup.fixtures.app import *
    from data.tests.setup.fixtures.internal_modules import *
    from data.tests.setup.fixtures.external_modules import *
    from data.service.helpers.responses import Responses

from shared.utils.tests.fixtures.models import *

API_PREFIX = '/api'


class TestUserManagementService:

    @pytest.mark.parametrize(
        "route,method",
        [
            pytest.param(
                f'{API_PREFIX}/token',
                'put',
                id="token_put",
            ),
            pytest.param(
                f'{API_PREFIX}/token',
                'delete',
                id="token_delete",
            ),
        ],
    )
    def test_routes_disallowed_methods(self, route, method, client):

        res = getattr(client, method)(route)

        assert res.status_code == 405

    @pytest.mark.parametrize(
        "user,response",
        [
            pytest.param(
                dict(username='username', password='password'),
                {"access_token": 'access_token'},
                id="existent-user",
            ),
            pytest.param(
                dict(username='non-user', password='password'),
                {"msg": "Wrong email or password"},
                id="non-existent-user",
            ),
        ],
    )
    def test_token_endpoint(
        self,
        user,
        response,
        client,
        create_user,
        mock_create_access_token_user_mgmt,
        mock_redis_connection_user_mgmt,
    ):
        res = client.post(f'{API_PREFIX}/token', json=user)

        assert res.json == jsonify(response).json

    @pytest.mark.parametrize(
        "user,response",
        [
            pytest.param(
                dict(username='username', password='password'),
                {"access_token": 'renewed_access_token'},
                id="renewed_access_token",
            ),
        ],
    )
    def test_token_endpoint_after_request(
        self,
        user,
        response,
        client,
        create_user,
        mock_create_access_token_user_mgmt,
        mock_redis_connection_user_mgmt,
        mock_get_jwt
    ):
        res = client.post(f'{API_PREFIX}/token', json=user)

        assert res.json == jsonify(response).json
