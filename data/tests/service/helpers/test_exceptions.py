import pytest

from data.service.helpers.exceptions import CandleSizeInvalid, CandleSizeRequired, ColorRequired, \
    DataPipelineCouldNotBeStopped, DataPipelineDoesNotExist, DataPipelineOngoing, ExchangeInvalid, ExchangeRequired, \
    LeverageInvalid, NameInvalid, NameRequired, ParamsInvalid, ParamsRequired, PipelineStartFail, SymbolRequired
from data.tests.setup.fixtures.internal_modules import mock_stop_instance, spy_stop_instance
from shared.utils.tests.fixtures.models import *

API_PREFIX = '/api'


arg = 'abc'


class TestExceptions:

    @pytest.mark.parametrize(
        "exception,message",
        [
            pytest.param(
                CandleSizeInvalid(),
                f"The candle size is not valid.",
                id="CandleSizeInvalid",
            ),
            pytest.param(
                CandleSizeRequired(),
                "A candle size must be included in the request.",
                id="CandleSizeRequired",
            ),
            pytest.param(
                ColorRequired(),
                "Parameter 'color' is required.",
                id="ColorRequired",
            ),
            pytest.param(
                DataPipelineCouldNotBeStopped(),
                f"The Pipeline could not be stopped",
                id="DataPipelineCouldNotBeStopped",
            ),
            pytest.param(
                DataPipelineDoesNotExist(),
                f"Provided data pipeline does not exist.",
                id="DataPipelineDoesNotExist",
            ),
            pytest.param(
                DataPipelineOngoing(),
                f"Provided data pipeline is already ongoing.",
                id="DataPipelineOngoing",
            ),
            pytest.param(
                ExchangeInvalid(),
                f"Exchange is not valid.",
                id="ExchangeInvalid",
            ),
            pytest.param(
                ExchangeRequired(),
                "An exchange must be included in the request.",
                id="ExchangeRequired",
            ),
            pytest.param(
                LeverageInvalid(),
                f"Leverage Invalid.",
                id="LeverageInvalid",
            ),
            pytest.param(
                NameInvalid(),
                f"Chosen name is not valid is already taken.",
                id="NameInvalid",
            ),
            pytest.param(
                NameRequired(),
                "A name must be included in the request.",
                id="NameRequired",
            ),
            pytest.param(
                ParamsInvalid(),
                f"Parameters are not valid.",
                id="ParamsInvalid",
            ),
            pytest.param(
                ParamsRequired(),
                "The strategy parameters must be included in the request.",
                id="ParamsRequired",
            ),
            pytest.param(
                PipelineStartFail(),
                f"Pipeline start failed.",
                id="PipelineStartFail",
            ),
            pytest.param(
                SymbolRequired(),
                "A symbol must be included in the request.",
                id="SymbolRequired",
            ),
        ],
    )
    def test_exceptions_without_args(self, exception, message):

        assert exception.message == message
        assert exception.__str__() == message
        assert exception.__repr__() == exception.__class__.__name__

    @pytest.mark.parametrize(
        "exception,message",
        [
            pytest.param(
                CandleSizeInvalid(arg),
                f"{arg} is not a valid candle size.",
                id="CandleSizeInvalid",
            ),
            pytest.param(
                CandleSizeRequired(arg),
                "A candle size must be included in the request.",
                id="CandleSizeRequired",
            ),
            pytest.param(
                ColorRequired(arg),
                "Parameter 'color' is required.",
                id="ColorRequired",
            ),
            pytest.param(
                DataPipelineCouldNotBeStopped(arg),
                f"Data pipeline could not be stopped. {arg}",
                id="DataPipelineCouldNotBeStopped",
            ),
            pytest.param(
                DataPipelineDoesNotExist(arg),
                f"Data pipeline {arg} does not exist.",
                id="DataPipelineDoesNotExist",
            ),
            pytest.param(
                DataPipelineOngoing(arg),
                f"Data pipeline {arg} is already ongoing.",
                id="DataPipelineOngoing",
            ),
            pytest.param(
                ExchangeInvalid(arg),
                f"{arg} is not a valid exchange.",
                id="ExchangeInvalid",
            ),
            pytest.param(
                ExchangeRequired(arg),
                "An exchange must be included in the request.",
                id="ExchangeRequired",
            ),
            pytest.param(
                LeverageInvalid(arg),
                f"{arg} is not a valid leverage.",
                id="LeverageInvalid",
            ),
            pytest.param(
                NameInvalid(arg),
                f"{arg} is not a valid name or is already taken.",
                id="NameInvalid",
            ),
            pytest.param(
                NameRequired(arg),
                "A name must be included in the request.",
                id="NameRequired",
            ),
            pytest.param(
                ParamsInvalid(arg),
                f"{arg} are not valid parameters.",
                id="ParamsInvalid",
            ),
            pytest.param(
                ParamsRequired(arg),
                f"{arg} are required parameters of the selected strategy.",
                id="ParamsRequired",
            ),
            pytest.param(
                PipelineStartFail(arg),
                f"Pipeline {arg} failed to start",
                id="PipelineStartFail",
            ),
            pytest.param(
                SymbolRequired(arg),
                "A symbol must be included in the request.",
                id="SymbolRequired",
            ),
        ],
    )
    def test_exceptions_with_args(self, exception, message):
        assert exception.message == message
        assert exception.__str__() == message
        assert exception.__repr__() == exception.__class__.__name__
