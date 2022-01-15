import json

ORDER_FORMAT_CONVERTER = dict(
    order_id="orderId",
    client_order_id="clientOrderId",
    symbol_id="symbol",
    transact_time="transactTime",
    price="price",
    original_qty="origQty",
    executed_qty="executedQty",
    cummulative_quote_qty="cummulativeQuoteQty",
    status="status",
    type="type",
    side="side",
    is_isolated="isIsolated",
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
