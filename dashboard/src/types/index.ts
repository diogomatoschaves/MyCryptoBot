

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
    pipelineName: string
    pipelineColor: string
    leverage: number
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
    pipelineName: string
    pipelineColor: string
    leverage: number
}


export type Pipeline = {
    id: number
    strategy: string
    params: Object
    candleSize: string
    name: string,
    equity: number,
    exchange: string
    symbol: string
    active: boolean
    paperTrading: boolean
    openTime: Date | null
    numberTrades: number
    profitLoss: number
    color: string
    leverage: number
}


export type RawPipeline = {
    id: number
    strategy: string
    params: Object
    candleSize: string
    name: string,
    equity: number,
    exchange: string
    symbol: string
    active: boolean
    paperTrading: boolean
    openTime: string | null
    numberTrades: number
    profitLoss: number
    color: string
    leverage: number
}

export type PipelineParams = {
    pipelineId?: number
    name: string,
    equity: number,
    leverage: number,
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
    leverage: number
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
    closeTime: string,
    leverage: number
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
    bottomProp: string,
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


export type PipelinesMetrics = {
    totalPipelines: number,
    activePipelines: number,
    bestWinRate: Partial<Pipeline> & {winRate: number},
    mostTrades: Partial<Pipeline> & {totalTrades: number},
    [key: string]: any;
}


export interface PipelinesObject {
    [key: string]: Pipeline
}


export interface TradesObject {
    [key: string]: Trade
}


export type TradesMetrics = {
    avgTradeDuration: number
    maxTradeDuration: number
    bestTrade: number
    worstTrade: number
    numberTrades: number
    winningTrades: number
    losingTrades: number
}

export type Data = {
    time: number | string
    $: number
}

export type PieChartData = {
    name: string
    value: number
    color: string
}

export type EquityTimeSeries = {
    live: Data[]
    test: Data[]
}

export type StartPipeline = (pipelineParams: PipelineParams) => Promise<void>
export type StopPipeline = (pipelineId: number) => Promise<void>
export type EditPipeline = (pipelineParams: PipelineParams, pipelineId?: number) => Promise<void>
export type DeletePipeline = (pipelineId: number) => Promise<void>
export type ChangeMenu = (option: MenuOption) => void
export type GetCurrentPrices = () => void
export type UpdateMessage = (newMessage: Object)  => void
export type UpdateTrades = (page?: number, pipelineId?: string)  => void
export type UpdatePipelinesMetrics = ()  => void
