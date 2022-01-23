
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
