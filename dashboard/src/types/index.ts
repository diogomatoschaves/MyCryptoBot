

export type DropdownOptions = {
    key: number,
    text: string,
    value?: number | undefined
}

export type Trade = {
    id: number,
    symbol: string,
    exchange: string
    base: string,
    quote: string,
    openTime: Date,
    closeTime: Date | null,
    openPrice: number,
    closePrice: number | null,
    profitLoss: number | null,
    amount: number,
    side: number
    mock: boolean
    pipelineId: number
}

export type RawTrade = {
    id: number,
    symbol: string,
    exchange: string
    base: string,
    quote: string,
    openTime: string,
    closeTime: string | null,
    openPrice: number,
    closePrice: number | null,
    profitLoss: number | null,
    amount: number,
    side: number
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
    openTime: Date | null
    numberTrades: number
    profitLoss: number
}


export type RawPipeline = {
    id: number
    strategy: string
    params: Object
    candleSize: string
    exchange: string
    symbol: string
    active: boolean
    paperTrading: boolean
    openTime: string | null
    numberTrades: number
    profitLoss: number
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


export type Message = {
    text: string | null,
    show: boolean,
    bottomProp: number,
    color: string,
    success: boolean
}

export type StartPipeline = (pipelineParams: PipelineParams) => void
export type StopPipeline = (pipelineId: number) => void
export type ChangeMenu = (option: MenuOption) => void
export type GetCurrentPrices = () => void