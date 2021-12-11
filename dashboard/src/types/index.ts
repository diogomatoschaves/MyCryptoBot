

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
    transactTime: Date,
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

export type RawOrder = {
    orderId: number,
    clientOrderId: number,
    symbol: string,
    base: string,
    quote: string,
    transactTime: string,
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
    params: Object
    candleSize: string
    exchange: string
    symbol: string
    active: boolean
    paperTrading: boolean
}

export type PipelineParams = {
    symbol: string
    strategy: string
    candleSize: string
    exchanges: string
    params: Object,
    paperTrading: boolean
}


export type MenuOption = {
    icon: string,
    emoji: string,
    text: string,
    code: string
}

export type StartPipeline = (pipelineParams: PipelineParams) => void
export type StopPipeline = (pipelineId: number) => void
export type ChangeMenu = (option: MenuOption) => void