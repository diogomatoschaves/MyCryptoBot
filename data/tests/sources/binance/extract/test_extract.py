from shared.utils.tests.fixtures.models import *
from shared.utils.tests.test_setup import get_fixtures
from data.sources.binance.extract import extract_data
from data.tests.setup.fixtures.external_modules import mock_get_historical_klines_generator

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

        symbol = fixture["in"]["symbol"]
        candle_size = fixture["in"]["candle_size"]

        params_dict = dict(
            get_klines_method=mock_get_historical_klines_generator,
            symbol=symbol,
            candle_size=candle_size,
            start_date=datetime.datetime(2023, 9, 1).replace(tzinfo=pytz.utc)
        )

        assert extract_data(**params_dict).equals(fixture["out"]["expected_value"])
