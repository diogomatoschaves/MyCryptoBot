import pytest


with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", True)
    from data.tests.setup.fixtures.app import *


class TestDataService:

    def test_index_route(self, client):

        res = client.get('/')

        assert res.data.decode(res.charset) == 'No files found!'
