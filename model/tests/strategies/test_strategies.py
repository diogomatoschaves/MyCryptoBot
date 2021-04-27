import os

import pytest

from model.tests.setup.test_data.sample_data import data
from shared.utils.tests.test_setup import get_fixtures

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path)


class TestStrategy:
    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_strategy_data(self, fixture):
        """
        GIVEN some params
        WHEN the method get_signal is called
        THEN the return value is equal to the expected response

        """

        params = fixture["in"]["params"]

        strategy = fixture["in"]["strategy"]

        instance = strategy(**params, data=data)

        assert instance.data.equals(fixture["out"]["expected_data"])

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_strategy_set_parameters(self, fixture):
        """
        GIVEN some params
        WHEN the method get_signal is called
        THEN the return value is equal to the expected response

        """

        params = fixture["in"]["params"]

        strategy = fixture["in"]["strategy"]
        new_parameters = fixture["in"]["new_parameters"]

        instance = strategy(**params, data=data)

        instance.set_parameters(new_parameters)

        assert instance.data.equals(fixture["out"]["expected_data_set_parameters"])

        for param, value in new_parameters.items():
            assert getattr(instance, f"_{param}") == value

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_strategy_get_signal(self, fixture):
        """
        GIVEN some params
        WHEN the method get_signal is called
        THEN the return value is equal to the expected response

        """

        params = fixture["in"]["params"]

        strategy = fixture["in"]["strategy"]

        instance = strategy(**params, data=data)

        assert instance.get_signal() == fixture["out"]["expected_signal"]
