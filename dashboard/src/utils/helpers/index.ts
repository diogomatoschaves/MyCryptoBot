import {
  DropdownOptions, EditPipeline,
  Pipeline,
  Position,
  RawPipeline,
  RawPosition,
  RawTrade,
  StartPipeline, Strategy,
  Trade
} from "../../types";
import {UPDATE_MESSAGE} from "../../reducers/modalReducer";

export const validatePipelineCreation = async (
    {
      name,
      equity,
      symbol,
      color,
      symbolsOptions,
      strategies,
      strategyCombination,
      dynamicStrategies,
      candleSize,
      candleSizeOptions,
      exchanges,
      exchangeOptions,
      startPipeline,
      updateModal,
      liveTrading,
      balance,
      leverage,
      edit,
      editPipeline,
      pipelineId
    }: {
      name: string | undefined,
      equity: string | undefined,
      symbol: number | undefined,
      color: string | undefined,
      symbolsOptions: DropdownOptions[],
      strategies: number[],
      strategyCombination: string,
      dynamicStrategies: Strategy[],
      candleSize: number | undefined,
      candleSizeOptions: DropdownOptions[],
      exchanges: Array<number>,
      exchangeOptions: DropdownOptions[],
      startPipeline: StartPipeline,
      updateModal: any,
      liveTrading: boolean,
      balance: number,
      leverage: number,
      edit?: boolean,
      editPipeline: EditPipeline,
      pipelineId?: number
    }) => {
  if (!name || !color || !equity || !symbol || strategies.length === 0 || !candleSize || exchanges.length === 0) {
    updateModal({
      type: UPDATE_MESSAGE,
      message: {text: "All parameters must be specified.", success: false}
    })
    return false
  }

  const equityFloat = Number(equity)

  if (!equityFloat) {
    updateModal({
      type: UPDATE_MESSAGE,
      message: {text: "Equity must be a number.", success: false}
    })
    return false
  }

  if (equityFloat > balance) {
    updateModal({
      type: UPDATE_MESSAGE,
      message: {text: `Chosen equity must be smaller than ${(balance).toFixed(1)} USDT`, success: false}
    })
    return false
  }

  const strategiesPayload = strategies.map((index: number) => {

    const strategy = dynamicStrategies.find(strategy => strategy.value === index)

    return {
      name: strategy?.strategyName,
      className: strategy?.className,
      params: Object.keys(strategy?.selectedParams).reduce((acc, param) => {
        const paramsObj = {
          ...strategy?.params,
          ...strategy?.optionalParams
        }

        return {
            ...acc,
            [param]: paramsObj[param].options ?
              paramsObj[param].options[strategy?.selectedParams[param]] :
              strategy?.selectedParams[param]
          }
      }, {})
    }
  })

  const payload = {
    symbol: symbol ? symbolsOptions[symbol - 1].text : "",
    strategy: strategiesPayload,
    strategyCombination,
    candleSize: candleSize ? candleSizeOptions[candleSize - 1].text : "",
    // TODO: Generalize this for any number of exchanges
    exchanges: exchanges.length > 0 ? exchangeOptions[exchanges[0] - 1].text : "",
    name,
    equity: equityFloat,
    leverage,
    paperTrading: !liveTrading,
    color
  }


  if (edit) {
    await editPipeline(payload, pipelineId)
  } else {
    await startPipeline(payload)
  }

  return true

}


export const validateParams = (strategy: any) => {

  const params = strategy.selectedParams

  const requiredParams = strategy.paramsOrder.reduce((reduced: any, param: string) => {

    if (!params.hasOwnProperty(param) || (params[param] === "")) {
      return {
        success: false,
        strategiesParameters: reduced.params
      }
    }

    let typedParam
    if (strategy.params[param].type) {
      typedParam = eval(strategy.params[param].type.func)(params[param])
      if (isNaN(typedParam) || typeof(typedParam) !== strategy.params[param].type.type) {
        return {
          success: false,
          params: reduced.params
        }
      }
    }

    return {
      success: reduced.success,
      params: {
        ...reduced.params,
        [param]: typedParam ? typedParam : params[param]
      }
    }
  }, {success: true, params: {}})

  const optionalParams = strategy.optionalParamsOrder.reduce((reduced: any, param: string) => {

    if (!params.hasOwnProperty(param)) {
      return {
        success: reduced.success,
        params: reduced.params
      }
    }

    const paramData = strategy.optionalParams[param]
    const paramValue = paramData.options ? paramData.options[params[param]] : params[param]

    let typedParam
    if (strategy.optionalParams[param].type) {
      const typedParam = eval(strategy.optionalParams[param].type.func)(paramValue)
      if (typedParam !== typedParam || typeof (typedParam) !== paramData.type.type) {
        return {
          success: reduced.success && false,
          params: reduced.params
        }
      }
    }

    return {
      success: reduced.success,
      strategiesParameters: {
        ...reduced.params,
        [param]: typedParam ? typedParam : paramValue
      }
    }
  }, {success: true, params: {}})

  return {
    success: requiredParams.success && optionalParams.success,
    updatedParams: {...requiredParams.params, ...optionalParams.params}
  }
}

export const organizePipeline = (pipeline: RawPipeline, strategiesOptions: Strategy[]): Pipeline => {

  return {
    ...pipeline,
    openTime: pipeline.openTime ? new Date(Date.parse(pipeline.openTime)) : null,
  }
}


export const parseTrade = (trade: RawTrade): Trade => {
    return {
      ...trade,
      openTime: new Date(Date.parse(trade.openTime)),
      closeTime: new Date(Date.parse(trade.closeTime)),
    }
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


export const timeFormatterDate = (date: Date, currentDate?: Date | null) => {

  currentDate = currentDate || new Date()

  // @ts-ignore
  let difference = currentDate - date;

  return timeFormatterDiff(difference)

}

export const timeFormatterDiff = (difference: number) => {
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

export const getRoi = (original: number, current: number, side: number, leverage: number) => {
  return (Math.exp(Math.log(current / original) * side) - 1) * leverage
}

export const capitalize = (s: string) => {
  return s[0].toUpperCase() + s.slice(1);
}

let options = {
  year: "numeric",
  month: "numeric",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
}

export const convertDate = (timeStamp: number) => {
  // @ts-ignore
  return new Date(timeStamp).toLocaleDateString('en-GB', options);
}

export const addLineBreaks = (text: string) => {
  const regex = /\s{2}/g;
  return text.replace(regex, '<br/>')
}
