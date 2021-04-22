import pytest
import os

from data.sources.binance.load import load_data
from data.tests.setup.fixtures.models import *
from shared.utils.test_setup import get_fixtures

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path)


class TestBinanceLoad:

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_load_data(self, fixture, exchange_data):

        params_dict = dict(
            model_class=fixture["in"]["model_class"],
            data=fixture["in"]["data"],
            count_updates=fixture["in"]["count_updates"]
        )

        assert load_data(**params_dict) == fixture["out"]["expected_value"]
