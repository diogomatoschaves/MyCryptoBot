import pytest
import os

from data.tests.helpers.mocks.models import *
from shared.utils.test_setup import get_fixtures
from data.sources.binance.extract import extract_data
from data.tests.helpers.mocks.modules import mock_get_historical_klines_generator

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path)


class TestBinanceExtract:

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_extract_data(self, fixture, exchange_data):

        model_class = fixture["in"]["model_class"]
        symbol = fixture["in"]["symbol"]
        base_candle_size = fixture["in"]["base_candle_size"]
        candle_size = fixture["in"]["candle_size"]

        params_dict = dict(
            model_class=model_class,
            klines_generator=mock_get_historical_klines_generator,
            symbol=symbol,
            base_candle_size=base_candle_size,
            candle_size=candle_size
        )

        assert extract_data(**params_dict).equals(fixture["out"]["expected_value"])
