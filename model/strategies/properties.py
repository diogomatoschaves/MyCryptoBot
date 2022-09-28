import importlib
import inspect
from typing import get_args

from shared.utils.helpers import get_extended_name

STRATEGIES_LOCATION = "model.strategies"

STRATEGIES = {}


def map_type(type_):
    if type_ in ['int', 'float']:
        return "number"
    elif type_ == 'str':
        return "string"


for name, cls in inspect.getmembers(importlib.import_module(STRATEGIES_LOCATION), inspect.isclass):

    required = {}
    optional = {}
    required_ordering = []
    optional_ordering = []

    params = inspect.signature(cls.__init__).parameters

    for param, props in params.items():

        if param in ["self", "data", "kwargs"]:
            continue

        is_required = False

        if props.default is inspect._empty:
            is_required = True

        if len(get_args(props.annotation)) != 0:
            param_info = {
                "type": map_type(type(get_args(props.annotation)[0]).__name__),
                "options": get_args(props.annotation),
            }
        else:
            param_info = {
                 "type": map_type(props.annotation.__name__)
            }

        if is_required:
            required_ordering.append(param)
            required[param] = param_info
        else:
            optional_ordering.append(param)
            optional[param] = param_info

    STRATEGIES[name] = {
        "name": get_extended_name(name),
        "params": required,
        "optionalParams": optional,
        "paramsOrder": required_ordering,
        "optionalParamsOrder": optional_ordering
    }
