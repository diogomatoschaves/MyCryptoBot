

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
    pipelineId: number
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
    pipelineId: number
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

export type Position = {
    position: number,
    symbol: string,
    exchange: string,
    pipelineId: number,
    paperTrading: boolean,
    price: number,
    amount: number,
    open: boolean,
    openTime: Date,
    closeTime: Date
}


export type RawPosition = {
    position: number,
    symbol: string,
    exchange: string,
    pipelineId: number,
    paperTrading: boolean,
    price: number,
    amount: number,
    open: boolean,
    openTime: string,
    closeTime: string
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