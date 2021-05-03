

export type DropdownOptions = {
    key: string,
    text: string,
    value: number
}

export type Order = {
    orderId: number,
    clientOrderId: number,
    symbol: string,
    base: string,
    quote: string,
    transactTime: number,
    price: number,
    origQty: number,
    executedQty: number,
    cummulativeQuoteQty: number,
    status: string
    type: string
    side: string
    isIsolated: boolean
    mock: boolean
}

export type ActivePipeline = {
    symbol: string
    strategy: string
    params: any
    candleSize: string
    exchange: string
}