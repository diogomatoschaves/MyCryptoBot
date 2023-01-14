from data.service.helpers.exceptions import CandleSizeInvalid
from data.tests.setup.fixtures.internal_modules import *
from data.tests.setup.fixtures.external_modules import *
# from data.tests.setup.fixtures.app import mock_client_env_vars
from data.tests.setup.test_data.sample_data import processed_historical_data
from shared.utils.exceptions import SymbolInvalid
from shared.utils.tests.test_setup import get_fixtures
from shared.utils.tests.fixtures.external_modules import *
from shared.utils.tests.fixtures.models import *
from database.model.models import ExchangeData, StructuredData, Jobs


@pytest.fixture
def common_fixture(
    mocker,
    mock_binance_handler_klines,
    mock_binance_client_init,
    mock_binance_client_ping,
    mock_binance_client_exchange_info,
    mock_binance_handler_websocket,
    mock_binance_websocket_start,
    mock_binance_websocket_stop,
    mock_binance_threaded_websocket,
    exchange_data,
    mock_redis_connection_binance,
    # mock_client_env_vars,
    mock_settings_env_vars,
    mock_start_stop_symbol_trading_success_true_binance_handler
):
    return


class TestBinanceDataHandler:

    @pytest.mark.parametrize(
        "input_params,output",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "candle_size": "1h",
                },
                {
                    "expected_number_objs_structured": 1,
                    "expected_number_objs_exchange": 15,
                    "expected_value": 2
                },
                id="1hNoPipelineID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "candle_size": "1h",
                    "pipeline_id": 1
                },
                {
                    "expected_number_objs_structured": 1,
                    "expected_number_objs_exchange": 15,
                    "expected_value": 2
                },
                id="1hWithPipelineID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "candle_size": "5m",
                },
                {
                    "expected_number_objs_structured": 14,
                    "expected_number_objs_exchange": 15,
                    "expected_value": 2
                },
                id="5mNoPipelineID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "candle_size": "5m",
                    "pipeline_id": 1
                },
                {
                    "expected_number_objs_structured": 14,
                    "expected_number_objs_exchange": 15,
                    "expected_value": 2
                },
                id="5mWithPipelineID",
            ),
        ],
    )
    def test_binance_data_handler(
        self,
        input_params,
        output,
        common_fixture,
        mock_trigger_signal_successfully,
        trigger_signal_spy,
    ):

        binance_data_handler = BinanceDataHandler(**input_params)
        binance_data_handler.start_data_ingestion()

        assert ExchangeData.objects.all().count() == output["expected_number_objs_exchange"]
        assert StructuredData.objects.all().count() == output["expected_number_objs_structured"]
        assert StructuredData.objects.first().open_time.date() == processed_historical_data[0]["open_time"].date()

        if "pipeline_id" in input_params:
            pipeline_id = input_params["pipeline_id"]
        else:
            pipeline_id = None

        assert trigger_signal_spy.call_args_list[-1][0] == (pipeline_id,)

        binance_data_handler.stop_data_ingestion()

        assert ExchangeData.objects.all().count() == output["expected_number_objs_exchange"] - 1
        assert StructuredData.objects.all().count() == output["expected_number_objs_structured"] - 1

    @pytest.mark.parametrize(
        "input_params,output",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "candle_size": "1h",
                    "pipeline_id": 1
                },
                {
                    "expected_number_objs_structured": 1,
                    "expected_number_objs_exchange": 14,
                    "expected_value": 2
                },
                id="BaseCaseWithPipelineID",
            ),
        ],
    )
    def test_binance_data_handler_failed_trigger_signal(
        self,
        input_params,
        output,
        common_fixture,
        mock_trigger_signal_fail,
        mock_redis_connection_external_requests,
        trigger_signal_spy,
        create_pipeline,
        create_open_position
    ):

        binance_data_handler = BinanceDataHandler(**input_params)
        binance_data_handler.start_data_ingestion()

        if "pipeline_id" in input_params:
            pipeline_id = input_params["pipeline_id"]
        else:
            pipeline_id = None

        assert trigger_signal_spy.call_args_list[-1][0] == (pipeline_id,)

        assert ExchangeData.objects.all().count() == output["expected_number_objs_exchange"] - 1
        assert StructuredData.objects.all().count() == output["expected_number_objs_structured"] - 1

        pipeline = Pipeline.objects.get(id=pipeline_id)
        assert pipeline.active is False

        position = Position.objects.get(pipeline_id=pipeline_id)
        assert position.open is False
        assert position.position == 0

    @pytest.mark.parametrize(
        "input_value,exception",
        [
            pytest.param(
                {
                    "symbol": "BTCUSD",
                    "candle_size": "5m"
                },
                SymbolInvalid,
                id="SymbolInvalid",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "candle_size": "ewrfe"
                },
                CandleSizeInvalid,
                id="CandleSizeInvalid",
            ),
        ],
    )
    def test_exception(
        self,
        input_value,
        exception,
        common_fixture
    ):

        with pytest.raises(Exception) as excinfo:
            binance_data_handler = BinanceDataHandler(**input_value)

        assert excinfo.type == exception
