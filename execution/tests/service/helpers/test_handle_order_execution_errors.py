import json
from unittest.mock import MagicMock

import pytest
from binance.exceptions import BinanceAPIException

import importlib

with pytest.MonkeyPatch().context() as ctx:
    ctx.setenv("TEST", "true")
    # the decorators package __init__ shadows the submodule name with the
    # function, so resolve the module itself for patching
    decorator_module = importlib.import_module(
        "execution.service.helpers.decorators.handle_order_execution_errors"
    )
    from execution.service.helpers.decorators import handle_order_execution_errors
    from execution.service.helpers.exceptions import NegativeEquity

from database.model.models import Pipeline
from shared.utils.tests.fixtures.models import (  # noqa: F401
    create_exchange, create_symbol, create_assets, create_pipeline,
)


def api_exception(code=-2019, msg="margin is insufficient"):
    response = MagicMock()
    response.text = json.dumps({"code": code, "msg": msg})
    return BinanceAPIException(response, 400, response.text)


@pytest.fixture
def mock_alert(mocker):
    return mocker.patch.object(decorator_module, "send_alert")


@pytest.mark.django_db
class TestHandleOrderExecutionErrors:

    @pytest.mark.parametrize("exception", [api_exception(), NegativeEquity(1)])
    def test_deactivation_paths_fire_critical_alert(self, exception, mock_alert, create_pipeline):
        trader = MagicMock()

        def failing_trade():
            raise exception

        response = handle_order_execution_errors(
            symbol="BTCUSDT", trader_instance=trader, header="", pipeline_id=1
        )(failing_trade)()

        assert response["success"] is False
        assert Pipeline.objects.get(id=1).active is False
        mock_alert.assert_called_once()
        assert mock_alert.call_args.kwargs["severity"] == "critical"
