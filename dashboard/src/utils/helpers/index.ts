import {DropdownOptions, StartPipeline} from "../../types";

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
      startPipeline
    }: {
      symbol: number | undefined,
      symbolsOptions: DropdownOptions[],
      strategy: number | undefined,
      strategiesOptions: DropdownOptions[],
      candleSize: number | undefined,
      candleSizeOptions: DropdownOptions[],
      exchanges: Array<number>,
      exchangeOptions: DropdownOptions[],
      startPipeline: StartPipeline
    }) => {
  if (!symbol || !strategy || !candleSize || exchanges.length === 0) {
    console.log("All parameters must be specified")
    return
  }

  startPipeline({
    // @ts-ignore
    symbol: symbolsOptions.find(option => symbol === option.value).text,
    // @ts-ignore
    strategy: strategiesOptions.find(option => strategy === option.value).text,
    // @ts-ignore
    candleSize: candleSizeOptions.find(option => candleSize === option.value).text,
    // @ts-ignore
    exchanges: exchangeOptions.find(option => exchanges[0] === option.value).text, // TODO: Generalize this for any number of exchanges
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