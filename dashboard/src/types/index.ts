

export type DropdownOptions = {
    key: number,
    text: string,
    value?: number | undefined
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

export type Pipeline = {
    id: number
    strategy: string
    params: string
    candleSize: string
    exchange: string
    symbol: string
    active: boolean
    paperTrading: boolean
}

export type ActivePipeline = {
    symbol: string
    strategy: string
    params?: any
    candleSize: string
    exchange: string
}

export type PipelineParams = {
    symbol: string
    strategy: string
    candleSize: string
    exchanges: string
}

export type StartPipeline = (pipelineParams: Pipeline) => void
export type StopPipeline = (pipelineId: number) => void
export type ChangeMenu = (option: string) => void