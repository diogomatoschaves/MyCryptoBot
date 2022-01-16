import json

TRADE_FORMAT_CONVERTER = dict(
    id="id",
    symbol_id="symbol",
    exchange_id="exchange",
    open_time="openTime",
    close_time="closeTime",
    open_price="openPrice",
    close_price="closePrice",
    profit_loss="profitLoss",
    amount="amount",
    type="type",
    side="side",
    mock="mock",
    pipeline_id="pipelineId",
)


PIPELINE_FORMAT_CONVERTER = dict(
    id={"name": "id", "value_converter": lambda value: value},
    strategy={"name": "strategy", "value_converter": lambda value: value},
    params={"name": "params", "value_converter": lambda value: json.loads(value)},
    interval={"name": "candleSize", "value_converter": lambda value: value},
    exchange_id={"name": "exchange", "value_converter": lambda value: value},
    symbol_id={"name": "symbol", "value_converter": lambda value: value},
    active={"name": "active", "value_converter": lambda value: value},
    paper_trading={"name": "paperTrading", "value_converter": lambda value: value}
)


POSITION_FORMAT_CONVERTER = dict(
    position="position",
    symbol_id="symbol",
    exchange_id="exchange",
    pipeline_id="pipelineId",
    paper_trading="paperTrading",
    buying_price="price",
    amount="amount",
    open="open",
    open_time="openTime",
    close_time="closeTime"
)
