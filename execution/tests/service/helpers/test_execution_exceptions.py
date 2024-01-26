import pytest

from execution.service.helpers.exceptions import LeverageSettingFail, NegativeEquity, NoSuchSymbol, NoUnits, \
    PipelineNotActive, SignalInvalid, SignalRequired, SymbolAlreadyTraded, SymbolNotBeingTraded, InsufficientBalance
from shared.utils.tests.fixtures.models import *


arg = 'abc'


class TestExceptions:

    @pytest.mark.parametrize(
        "exception,message",
        [
            pytest.param(
                LeverageSettingFail(),
                "Failed to set leverage.",
                id="LeverageSettingFail",
            ),
            pytest.param(
                NegativeEquity(),
                "Pipeline has reached negative equity.",
                id="NegativeEquity",
            ),
            pytest.param(
                NoSuchSymbol(),
                f"Symbol was not found.",
                id="NoSuchSymbol",
            ),
            pytest.param(
                NoUnits(),
                f"Can't close position with 0 units.",
                id="NoUnits",
            ),
            pytest.param(
                PipelineNotActive(),
                "Pipeline is not active.",
                id="PipelineNotActive",
            ),
            pytest.param(
                SignalInvalid(),
                f"Signal is not valid.",
                id="SignalInvalid",
            ),
            pytest.param(
                SignalRequired(),
                "Parameter 'signal' is required.",
                id="SignalRequired",
            ),
            pytest.param(
                SymbolAlreadyTraded(),
                "Symbol is already being traded.",
                id="SymbolAlreadyTraded",
            ),
            pytest.param(
                SymbolNotBeingTraded(),
                f"Symbol is not being traded.",
                id="SymbolNotBeingTraded",
            ),
            pytest.param(
                InsufficientBalance(),
                f"Insufficient balance for starting pipeline.",
                id="InsufficientBalance",
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
                LeverageSettingFail(arg),
                f"Failed to set leverage. {arg}",
                id="LeverageSettingFail",
            ),
            pytest.param(
                NegativeEquity(arg),
                f"Pipeline {arg} has reached negative equity.",
                id="NegativeEquity",
            ),
            pytest.param(
                NoSuchSymbol(arg),
                f"Symbol {arg} was not found.",
                id="NoSuchSymbol",
            ),
            pytest.param(
                NoUnits(arg),
                f"Can't close position with 0 units.",
                id="NoUnits",
            ),
            pytest.param(
                PipelineNotActive(arg),
                f"Pipeline {arg} is not active.",
                id="PipelineNotActive",
            ),
            pytest.param(
                SignalInvalid(arg),
                f"{arg} is not a valid signal.",
                id="SignalInvalid",
            ),
            pytest.param(
                SignalRequired(arg),
                "Parameter 'signal' is required.",
                id="SignalRequired",
            ),
            pytest.param(
                SymbolAlreadyTraded(arg),
                f"{arg} is already being traded.",
                id="SymbolAlreadyTraded",
            ),
            pytest.param(
                SymbolNotBeingTraded(arg),
                f"{arg} is not being traded.",
                id="SymbolNotBeingTraded",
            ),
            pytest.param(
                InsufficientBalance(2000, 1000),
                f"Insufficient balance for starting pipeline. 2000 USDT is required and current balance is 1000 USDT.",
                id="InsufficientBalance",
            ),
        ],
    )
    def test_exceptions_with_args(self, exception, message):
        assert exception.message == message
        assert exception.__str__() == message
        assert exception.__repr__() == exception.__class__.__name__
