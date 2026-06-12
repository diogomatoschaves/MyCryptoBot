import pytest


with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from data.tests.setup.fixtures.app import *


class TestDataService:

    def test_index_route(self, client):

        res = client.get('/')

        assert res.data.decode(res.charset) == 'No files found!'

    def test_set_service_token_populates_cache(self, app):
        import data.service.app as data_app

        data_app.cache.delete("service_bearer_token")
        data_app.set_service_token(app)

        assert data_app.cache.get("service_bearer_token") == "Bearer abc"
