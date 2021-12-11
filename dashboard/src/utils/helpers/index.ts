import {DropdownOptions, Order, RawOrder, StartPipeline} from "../../types";
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


export const organizeOrders = (orders: RawOrder[]): Order[] => {

  return orders.map((order) => {
    return {
      ...order,
      transactTime: new Date(Date.parse(order.transactTime))
    }
  }).sort((a, b) => {
    return b.transactTime.getTime() - a.transactTime.getTime()
  })
}