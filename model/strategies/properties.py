import importlib
import inspect

from shared.utils.helpers._helpers import get_extended_name

STRATEGIES_LOCATION = "model.strategies"

STRATEGIES = {}


for name, cls in inspect.getmembers(importlib.import_module(STRATEGIES_LOCATION), inspect.isclass):

    required = []
    optional = []

    params = inspect.signature(cls.__init__).parameters

    for param, props in params.items():

        if param in ["self", "data", "kwargs"]:
            continue

        if props.default is inspect._empty:
            required.append(param)

        else:
            optional.append(param)

    STRATEGIES[name] = {
        "name": get_extended_name(name),
        "params": required,
        "optional_params": optional
    }
