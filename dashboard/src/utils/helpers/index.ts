import {DropdownOptions, Trade, Position, RawTrade, RawPosition, StartPipeline} from "../../types";
import PipelinePanel from "../../components/PipelinePanel";

export const validatePipelineCreation = (
    {
      symbol,
      symbolsOptions,
      strategy,
      strategiesOptions,
      candleSize,
      candleSizeOptions,
      exchanges,
      exchangeOptions,
      startPipeline,
      params,
      liveTrading
    }: {
      symbol: number | undefined,
      symbolsOptions: DropdownOptions[],
      strategy: number | undefined,
      strategiesOptions: DropdownOptions[],
      candleSize: number | undefined,
      candleSizeOptions: DropdownOptions[],
      exchanges: Array<number>,
      exchangeOptions: DropdownOptions[],
      startPipeline: StartPipeline,
      params: Object,
      liveTrading: boolean
    }) => {
  if (!symbol || !strategy || !candleSize || exchanges.length === 0) {
    console.log("All parameters must be specified")
    return
  }

  startPipeline({
    symbol: symbol ? symbolsOptions[symbol - 1].text : "",
    strategy: strategy ? strategiesOptions[strategy - 1].text : "",
    candleSize: candleSize ? candleSizeOptions[candleSize - 1].text : "",
    // TODO: Generalize this for any number of exchanges
    exchanges: exchanges.length > 0 ? exchangeOptions[exchanges[0] - 1].text : "",
    params,
    paperTrading: !liveTrading
  })
}


export const validateParams = (resolve: any, reject: any, params: any, strategy: any) => {
  [...strategy.params, ...strategy.optional_params].forEach((param) => {
    if (!params.hasOwnProperty(param) || params[param] === "") {
      return reject()
    }
  })
  return resolve()
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


export const timeFormatter = (date: Date) => {

  const currentDate = new Date()

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
