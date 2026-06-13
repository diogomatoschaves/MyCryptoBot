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

    def test_token_endpoint_sets_cookie(
        self,
        client,
        create_user,
        mock_redis_connection_user_mgmt,
    ):
        res = client.post(
            f'{API_PREFIX}/token', json=dict(username='username', password='password')
        )

        # the JWT is delivered as an httpOnly cookie, not in the body
        assert res.status_code == 200
        assert res.json == {"login": True, "username": "username"}
        assert "access_token" not in res.json
        assert any(
            "access_token_cookie" in header
            for header in res.headers.getlist("Set-Cookie")
        )

    def test_token_endpoint_wrong_credentials(
        self,
        client,
        create_user,
        mock_redis_connection_user_mgmt,
    ):
        res = client.post(
            f'{API_PREFIX}/token', json=dict(username='non-user', password='password')
        )

        assert res.status_code == 401
        assert res.json == {"msg": "Wrong email or password"}

    def test_logout_clears_cookie(self, client, mock_redis_connection_user_mgmt):
        res = client.post(f'{API_PREFIX}/logout')

        assert res.status_code == 200
        assert res.json == {"logout": True}
        # the access cookie is unset (cleared) on logout
        assert any(
            "access_token_cookie=;" in header
            for header in res.headers.getlist("Set-Cookie")
        )
