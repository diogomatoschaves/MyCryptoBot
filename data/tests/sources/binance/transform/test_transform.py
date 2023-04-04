import pytest
import numpy as np
import pandas as pd

from data.sources.binance.transform import transform_data
from shared.utils.tests.fixtures.models import *
from shared.utils.tests.test_setup import get_fixtures

current_path = os.path.dirname(os.path.realpath(__file__))

fixtures = get_fixtures(current_path)


class TestBinanceTransform:

    @pytest.mark.parametrize(
        "fixture",
        [
            pytest.param(fixture, id=fixture_name)
            for fixture_name, fixture in fixtures.items()
        ],
    )
    def test_transform_data(self, fixture):

        params_dict = dict(
            data=fixture["in"]["data"],
            candle_size=fixture["in"]["candle_size"],
            exchange=fixture["in"]["exchange"],
            symbol=fixture["in"]["symbol"],
            aggregation_method=fixture["in"]["aggregation_method"],
            is_removing_zeros=fixture["in"]["is_removing_zeros"],
            is_removing_rows=fixture["in"]["is_removing_rows"]
        )

        result = transform_data(**params_dict).reset_index().to_dict(orient='records')

        for i, d in enumerate(result):
            for key in d:
                if pd.isna(d[key]):
                    assert np.isnan(fixture["out"]["expected_value"][i][key])
                else:
                    assert d[key] == pytest.approx(fixture["out"]["expected_value"][i][key], 0.2)
