import json
import os

import pytest
import pandas as pd

from model.strategies.properties import compile_strategies
from model.tests.setup.test_data.sample_data import data
from model.tests.setup.fixtures.internal_modules import spy_download_file
from model.tests.setup.fixtures.external_modules import (
    mock_boto3_client,
    mock_boto3_client_raise_client_error,
    mock_boto3_client_raise_no_credentials_error
)
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

        pd.testing.assert_frame_equal(instance.data, fixture["out"]["expected_data"], check_exact=False)

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

        pd.testing.assert_frame_equal(instance.data, fixture["out"]["expected_data_set_parameters"], check_exact=False)

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

    def test_compile_strategies(self, mock_boto3_client, spy_download_file):
        strategies = compile_strategies()

        json.dumps(strategies)

        assert spy_download_file.call_count == 2

    def test_compile_strategies_raise_client_error(
        self,
        mock_boto3_client_raise_client_error,
        spy_download_file
    ):
        strategies = compile_strategies()

        json.dumps(strategies)

        assert spy_download_file.call_count == 0

    def test_compile_strategies_raise_no_credentials_error(
        self,
        mock_boto3_client_raise_no_credentials_error,
        spy_download_file
    ):
        strategies = compile_strategies()

        json.dumps(strategies)

        assert spy_download_file.call_count == 0
