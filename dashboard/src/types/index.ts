

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
    closeTime: Date,
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
    closeTime: string,
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
    name: string,
    allocation: number,
    exchange: string
    symbol: string
    active: boolean
    paperTrading: boolean
    openTime: Date | null
    numberTrades: number
    profitLoss: number
    color: string
}


export type RawPipeline = {
    id: number
    strategy: string
    params: Object
    candleSize: string
    name: string,
    allocation: number,
    exchange: string
    symbol: string
    active: boolean
    paperTrading: boolean
    openTime: string | null
    numberTrades: number
    profitLoss: number
    color: string
}

export type PipelineParams = {
    name: string,
    allocation: number,
    symbol: string
    strategy: string
    candleSize: string
    exchanges: string
    params: Object,
    paperTrading: boolean,
    color: string
}

export type Position = {
    position: number,
    symbol: string,
    exchange: string,
    pipelineId: number,
    pipelineName: string,
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
    pipelineName: string,
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


export type Balance = {
    availableBalance: number,
    totalBalance: number
}

export type BalanceObj = {
    live: {
        USDT: Balance
    },
    test: {
        USDT: Balance
    }
}

export type Decimals = {
    quoteDecimal: number,
    baseDecimal: number
}

export type StartPipeline = (pipelineParams: PipelineParams) => void
export type StopPipeline = (pipelineId: number) => Promise<void>
export type DeletePipeline = (pipelineId: number) => void
export type ChangeMenu = (option: MenuOption) => void
export type GetCurrentPrices = () => void
export type UpdateMessage = (text: string, success: boolean)  => void