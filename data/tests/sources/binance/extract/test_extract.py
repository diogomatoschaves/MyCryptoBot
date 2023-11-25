from shared.utils.tests.fixtures.models import *
from shared.utils.tests.test_setup import get_fixtures
from data.sources.binance.extract import extract_data, get_latest_date
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

    @pytest.mark.parametrize(
        "symbol,upper_date_limit,expected_output",
        [
            pytest.param(
                "BTCUSDT",
                datetime.datetime(2023, 9, 1, 11).replace(tzinfo=pytz.utc),
                datetime.datetime(2023, 9, 1, 11).replace(tzinfo=pytz.utc),
                id="with-upper-date-limit",
            ),
            pytest.param(
                "BTCUSDT",
                None,
                datetime.datetime(2023, 9, 1, 12).replace(tzinfo=pytz.utc),
                id="with-upper-date-limit",
            ),
            pytest.param(
                "USDT",
                datetime.datetime(2023, 9, 1, 10).replace(tzinfo=pytz.utc),
                datetime.datetime(2023, 9, 1, 10).replace(tzinfo=pytz.utc),
                id="with-upper-date-limit",
            ),
            pytest.param(
                "USDT",
                None,
                None,
                id="with-upper-date-limit",
            ),
        ],
    )
    def test_get_latest_date(self, symbol, upper_date_limit, expected_output, populate_exchange_data):
        candle_size = '1h'

        output = get_latest_date(ExchangeData, symbol, candle_size=candle_size, upper_date_limit=upper_date_limit)

        assert output == expected_output
