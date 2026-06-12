import os

import pandas as pd

from data.sources.binance.load import load_data
from data.tests.setup.test_data.sample_data import (
    exchange_data_1, exchange_data_2, exchange_data_3,
)
from database.model.models import ExchangeData
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.test_setup import get_fixtures

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
    def test_load_data(self, fixture, exchange_data, create_pipeline):

        params_dict = dict(
            model_class=fixture["in"]["model_class"],
            data=fixture["in"]["data"],
            update_duplicate=fixture["in"]["count_updates"],
            pipeline_id=1
        )

        assert load_data(**params_dict) == fixture["out"]["expected_value"]

    def test_bulk_load_mixed_new_and_duplicate(self, exchange_data, create_pipeline):
        # exchange_data fixture pre-creates exchange_data_1; the batch mixes
        # that duplicate with two genuinely new rows
        data = pd.DataFrame([exchange_data_1, exchange_data_2, exchange_data_3])

        new_entries = load_data(
            ExchangeData, data, pipeline_id=1, update_duplicate=True
        )

        # 2 new + 1 replaced duplicate, and no row was doubled
        assert new_entries == 3
        assert ExchangeData.objects.count() == 3

    def test_bulk_load_skips_duplicates_when_not_updating(self, exchange_data, create_pipeline):
        data = pd.DataFrame([exchange_data_1, exchange_data_2, exchange_data_3])

        new_entries = load_data(
            ExchangeData, data, pipeline_id=1, update_duplicate=False
        )

        # only the 2 new rows count; the duplicate is left untouched
        assert new_entries == 2
        assert ExchangeData.objects.count() == 3
