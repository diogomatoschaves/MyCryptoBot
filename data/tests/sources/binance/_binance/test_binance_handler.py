import datetime

import pandas as pd

from data.service.helpers.exceptions import CandleSizeInvalid
from data.sources.binance import get_historical_data
from data.tests.setup.fixtures.internal_modules import *
from data.tests.setup.fixtures.external_modules import *
from data.tests.setup.test_data.sample_data import processed_historical_data_5m, processed_historical_data_5m_2
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
    # exchange_data,
    populate_structured_data,
    mock_redis_connection_binance,
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
                    "expected_number_objs_structured": 2,
                    "expected_number_objs_exchange": 14,
                    "expected_times_called": 2
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
                    "expected_number_objs_structured": 2,
                    "expected_number_objs_exchange": 14,
                    "expected_times_called": 2
                },
                id="1hWithPipelineID",
            ),
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "candle_size": "5m",
                },
                {
                    "expected_number_objs_structured": 16,
                    "expected_number_objs_exchange": 14,
                    "expected_times_called": 2
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
                    "expected_number_objs_structured": 16,
                    "expected_number_objs_exchange": 14,
                    "expected_times_called": 2
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
        spy_binance_handler_klines
    ):

        input_params["start_date"] = datetime.datetime(2023, 9, 1).replace(tzinfo=pytz.utc)

        print(ExchangeData.objects.all().values())
        print(StructuredData.objects.all().values())

        binance_data_handler = BinanceDataHandler(**input_params)
        binance_data_handler.start_data_ingestion()

        print(ExchangeData.objects.count())
        print(StructuredData.objects.count())

        assert ExchangeData.objects.all().count() == output["expected_number_objs_exchange"]

        assert StructuredData.objects.all().count() == output["expected_number_objs_structured"]
        assert StructuredData.objects.first().open_time.date() == processed_historical_data_5m[0]["open_time"].date()

        if "pipeline_id" in input_params:
            pipeline_id = input_params["pipeline_id"]
        else:
            pipeline_id = None

        assert trigger_signal_spy.call_args_list[-1][0] == (pipeline_id,)
        assert spy_binance_handler_klines.call_count == output["expected_times_called"]

        binance_data_handler.stop_data_ingestion()

        assert ExchangeData.objects.all().count() == output["expected_number_objs_exchange"] - 1
        assert StructuredData.objects.all().count() == output["expected_number_objs_structured"] - 1

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "input_params,output",
        [
            pytest.param(
                {
                    "symbol": "BTCUSDT",
                    "candle_size": "1h",
                    "pipeline_id": 2
                },
                {
                    "expected_number_objs_structured": 1,
                    "expected_number_objs_exchange": 13,
                    "expected_value": 1
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
        create_open_position
    ):

        input_params["start_date"] = datetime.datetime(2023, 9, 1, tzinfo=pytz.utc)

        print(ExchangeData.objects.all().count())
        print(StructuredData.objects.all().count())

        binance_data_handler = BinanceDataHandler(**input_params)
        binance_data_handler.start_data_ingestion()

        if "pipeline_id" in input_params:
            pipeline_id = input_params["pipeline_id"]
        else:
            pipeline_id = None

        assert trigger_signal_spy.call_args_list[-1][0] == (pipeline_id,)

        assert ExchangeData.objects.all().count() == output["expected_number_objs_exchange"] - 1
        assert StructuredData.objects.all().count() == output["expected_number_objs_structured"]

        pipeline = Pipeline.objects.get(id=pipeline_id)
        assert pipeline.active is False

        position = Position.objects.get(pipeline_id=pipeline_id)
        assert position.open is False
        assert position.position == 0

    @pytest.mark.parametrize(
        "pipeline_id,exception,start_stop_symbol_return_value,expected_values",
        [
            pytest.param(
                2,
                False,
                {"success": True, "message": ''},
                {
                    "pipeline_active": False,
                    "position_active": False,
                    "position_side": 0,
                },
                id="start_stop-True",
            ),
            pytest.param(
                2,
                False,
                {"success": False, "message": ''},
                {
                    "pipeline_active": True,
                    "position_active": True,
                    "position_side": 1,
                },
                id="start_stop-False",
            ),
            pytest.param(
                11,
                False,
                {"success": True, "message": ''},
                {
                    "pipeline_active": False,
                    "position_active": False,
                    "position_side": 0,
                },
                id="start_stop-True|paper_trading",
            ),
            pytest.param(
                11,
                False,
                {"success": False, "message": ''},
                {
                    "pipeline_active": True,
                    "position_active": True,
                    "position_side": 0,
                },
                id="start_stop-False|paper_trading",
            ),
            pytest.param(
                2,
                True,
                {"success": False, "message": 'API ERROR'},
                {
                    "pipeline_active": True,
                    "position_active": True,
                    "position_side": 1,
                },
                id="start_stop-False|raise_exception",
            ),
        ],
    )
    def test_binance_data_handler_stop_pipeline_fail(
        self,
        pipeline_id,
        exception,
        start_stop_symbol_return_value,
        expected_values,
        common_fixture,
        create_open_position,
        create_open_position_paper_trading_pipeline,
        mock_trigger_signal_successfully,
        mock_start_stop_symbol_trading,
        mock_get_open_positions,
        mock_redis_connection_external_requests,
        create_paper_trading_pipeline
    ):
        input_params = {
            "symbol": "BTCUSDT",
            "candle_size": "1h",
            "pipeline_id": pipeline_id
        }

        mock_start_stop_symbol_trading.return_value = start_stop_symbol_return_value

        if exception:
            with pytest.raises(Exception) as exception:
                binance_data_handler = BinanceDataHandler(**input_params)
                binance_data_handler.start_data_ingestion()
                binance_data_handler.stop_data_ingestion(raise_exception=True)

            assert exception.type == DataPipelineCouldNotBeStopped

        else:
            binance_data_handler = BinanceDataHandler(**input_params)
            binance_data_handler.start_data_ingestion()
            binance_data_handler.stop_data_ingestion()

        pipeline = Pipeline.objects.get(id=pipeline_id)

        assert pipeline.active is expected_values["pipeline_active"]

        position = Position.objects.get(pipeline_id=pipeline_id)
        assert position.open is expected_values["position_active"]
        assert position.position == expected_values["position_side"]

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

    def test_get_historical_data(
        self,
        common_fixture,
        tmp_path
    ):
        historical_data = get_historical_data(
            'BTCUSDT',
            '5m',
            "2023-09-01 14:00",
            end_date="2023-09-01 15:00",
            batch_size=1000,
            save_file=True,
            directory=tmp_path
        )

        df = historical_data.reset_index()
        data_records = df.to_dict(orient='records')

        for i, record in enumerate(data_records):
            for column, column_value in record.items():
                assert processed_historical_data_5m_2[i][column] == column_value
