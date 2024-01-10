import numpy as np
import pandas as pd
import pytest

from model.backtesting.helpers.margin import get_maintenance_margin, calculate_margin_ratio, calculate_liquidation_price
from model.tests.setup.test_data.sample_data import binance_margin_brackets


@pytest.mark.parametrize(
    "notional_value,result",
    [
        pytest.param(
            [10000],
            ([0.004], [0]),
            id='bracket_1'
        ),
        pytest.param(
            [100000],
            ([0.005], [50.0]),
            id='bracket_2'
        ),
        pytest.param(
            [1000000],
            ([0.01], [1300.0]),
            id='bracket_3'
        ),
        pytest.param(
            [10000000],
            ([0.025], [46300.0]),
            id='bracket_4'
        ),
        pytest.param(
            [10000000, 30, 200000, 100000000],
            ([0.025, 0.004, 0.005, 0.125], [46300., 0., 50., 5.0463e+06]),
            id='bracket_multiple'
        ),
        pytest.param(
            pd.Series([10000000, 30, 200000, 100000000]),
            ([0.025, 0.004, 0.005, 0.125], [46300., 0., 50., 5.0463e+06]),
            id='bracket_multiple_input_series'
        )
    ],
)
def test_get_maintenance_margin(notional_value, result):

    maintenance_margin = get_maintenance_margin(pd.DataFrame(binance_margin_brackets), notional_value, 'binance')

    print(maintenance_margin)

    for i, result_series in enumerate(maintenance_margin):
        for j, entry in enumerate(result_series):
            assert result[i][j] == entry


@pytest.mark.parametrize(
    "leverage,mark_price,side,result",
    [
        pytest.param(
            1,
            9000,
            1,
            0.001,
            id='case_1'
        ),
        pytest.param(
            5,
            9000,
            1,
            0.009,
            id='case_2'
        ),
        pytest.param(
            10,
            9000,
            1,
            np.Inf,
            id='case_3'
        ),
    ],
)
def test_calculate_margin_ratio(leverage, mark_price, side, result):

    maintenance_rate = 0.001
    maintenance_amount = 0

    entry_price = 10000
    units = 1

    margin_ratio = calculate_margin_ratio(
        leverage,
        units,
        side,
        entry_price,
        mark_price,
        maintenance_rate,
        maintenance_amount,
        exchange='binance'
    )

    assert margin_ratio == result


@pytest.mark.parametrize(
    "leverage,side,result",
    [
        pytest.param(
            1,
            1,
            0,
            id='leverage==1|side==1'
        ),
        pytest.param(
            1,
            -1,
            19920.32,
            id='leverage==1|side==-1'
        ),
        pytest.param(
            10,
            1,
            9036.14,
            id='leverage==10|side==1'
        ),
        pytest.param(
            10,
            -1,
            10956.18,
            id='leverage==10|side==-1'
        ),
        pytest.param(
            50,
            1,
            9839.36,
            id='leverage==50|side==1'
        ),
        pytest.param(
            50,
            -1,
            10159.36,
            id='leverage==50|side==-1'
        ),
    ],
)
def test_calculate_liquidation_price(leverage, side, result):

    maintenance_rate = 0.004
    maintenance_amount = 0

    entry_price = 10000
    units = 1

    liquidation_price = calculate_liquidation_price(
        units,
        entry_price,
        side,
        leverage,
        maintenance_rate,
        maintenance_amount,
        exchange='binance'
    )

    assert round(liquidation_price, 2) == result


@pytest.mark.parametrize(
    "params,method",
    [
        pytest.param(
            [binance_margin_brackets, [1000], 'non_existent_exchange'],
            get_maintenance_margin,
            id='get_maintenance_margin'
        ),
        pytest.param(
            [1, 1, -1, 1000, 1010, 0.004, 0, 'non_existent_exchange'],
            calculate_margin_ratio,
            id='calculate_margin_ratio'
        ),
        pytest.param(
            [1, 1000, 1, 10, 0.004, 0, 'non_existent_exchange'],
            calculate_liquidation_price,
            id='calculate_liquidation_price'
        ),
    ],
)
def test_non_existent_exchange(params, method):

    with pytest.raises(Exception) as exception:
        method(*params)
