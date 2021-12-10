

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
)


PIPELINE_FORMAT_CONVERTER = dict(
    id="id",
    strategy="strategy",
    params="params",
    interval="candleSize",
    exchange_id="exchange",
    symbol_id="symbol",
    active="active",
    paper_trading="paperTrading"
)
