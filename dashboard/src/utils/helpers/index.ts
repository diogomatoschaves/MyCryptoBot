import {
  DropdownOptions,
  Trade,
  Position,
  RawTrade,
  RawPosition,
  StartPipeline,
  RawPipeline,
  Pipeline, UpdateMessage
} from "../../types";

export const validatePipelineCreation = async (
    {
      name,
      allocation,
      symbol,
      symbolsOptions,
      strategy,
      strategiesOptions,
      candleSize,
      candleSizeOptions,
      exchanges,
      exchangeOptions,
      startPipeline,
      dispatch,
      params,
      liveTrading
    }: {
      name: string | undefined,
      allocation: string | undefined,
      symbol: number | undefined,
      symbolsOptions: DropdownOptions[],
      strategy: number | undefined,
      strategiesOptions: DropdownOptions[],
      candleSize: number | undefined,
      candleSizeOptions: DropdownOptions[],
      exchanges: Array<number>,
      exchangeOptions: DropdownOptions[],
      startPipeline: StartPipeline,
      dispatch: any,
      params: Object,
      liveTrading: boolean
    }) => {
  if (!name || !allocation || !symbol || !strategy || !candleSize || exchanges.length === 0) {
    dispatch({
      type: "UPDATE_MESSAGE",
      message: {text: "All parameters must be specified.", success: false}
    })
    return false
  }

  const allocationNumber = Number(allocation)

  if (!allocationNumber) {
    dispatch({
      type: "UPDATE_MESSAGE",
      message: {text: "Allocated capital must be a number.", success: false}
    })
    return false
  }

  startPipeline({
    symbol: symbol ? symbolsOptions[symbol - 1].text : "",
    strategy: strategy ? strategiesOptions[strategy - 1].text : "",
    candleSize: candleSize ? candleSizeOptions[candleSize - 1].text : "",
    // TODO: Generalize this for any number of exchanges
    exchanges: exchanges.length > 0 ? exchangeOptions[exchanges[0] - 1].text : "",
    params,
    name,
    allocation: allocationNumber,
    paperTrading: !liveTrading
  })

  return true
}


export const validateParams = (resolve: any, reject: any, params: any, strategy: any) => {
  [...strategy.params, ...strategy.optional_params].forEach((param) => {
    if (!params.hasOwnProperty(param) || params[param] === "") {
      return reject()
    }
  })
  return resolve()
}


export const organizePipelines = (pipelines: RawPipeline[]): Pipeline[] => {

  return pipelines.map((pipeline) => {
    return {
      ...pipeline,
      openTime: pipeline.openTime ? new Date(Date.parse(pipeline.openTime)) : null,
    }
  })
}


export const organizeTrades = (trades: RawTrade[]): Trade[] => {

  return trades.map((trade) => {
    return {
      ...trade,
      openTime: new Date(Date.parse(trade.openTime)),
      closeTime: trade.closeTime ? new Date(Date.parse(trade.closeTime)) : null,
    }
  }).sort((a, b) => {
    return b.openTime.getTime() - a.openTime.getTime()
  })
}


export const organizePositions = (positions: RawPosition[]): Position[] => {

  return positions.map((position) => {
    return {
      ...position,
      openTime: new Date(Date.parse(position.openTime)),
      closeTime: new Date(Date.parse(position.closeTime))
    }
  }).sort((a, b) => {
    return b.openTime.getTime() - a.openTime.getTime()
  })
}


export const timeFormatter = (date: Date, currentDate?: Date | null) => {

  currentDate = currentDate || new Date()

  // @ts-ignore
  let difference = currentDate - date;

  const days = Math.floor(difference/1000/60/60/24);
  difference -= days*1000*60*60*24;

  const hours = Math.floor(difference/1000/60/60);
  difference -= hours*1000*60*60;

  const minutes = Math.floor(difference/1000/60);

  if (days) {
    return `${days}d ${hours}h ${minutes}m`
  } else if (hours) {
    return `${hours}h ${minutes}m`
  } else {
    return `${minutes}m`
  }
}
