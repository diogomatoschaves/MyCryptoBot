import {Pipeline, RawStrategy, Strategy} from "../types";

export const UPDATE_STRATEGY = 'UPDATE_STRATEGY'
export const UPDATE_SECOND_MODAL_OPEN = 'UPDATE_SECOND_MODAL_OPEN'
export const RESET_MODAL = 'RESET_MODAL'
export const UPDATE_STRATEGY_PARAMS = 'UPDATE_STRATEGY_PARAMS'
export const UPDATE_PARAMS = 'UPDATE_PARAMS'
export const UPDATE_CHECKBOX = 'UPDATE_CHECKBOX'
export const UPDATE_MESSAGE = 'UPDATE_MESSAGE'
export const UPDATE_SECONDARY_MESSAGE = 'UPDATE_SECONDARY_MESSAGE'
export const GET_INITIAL_STATE = 'GET_INITIAL_STATE'
export const UPDATE_STRATEGY_COMBINATION = 'UPDATE_STRATEGY_COMBINATION'


export const modalReducer = (state: any, action: any) => {

  switch (action.type) {

    case UPDATE_STRATEGY:

      const strategyKeys = state.dynamicStrategies.map((strategy: Strategy) => strategy.value)
      const strategyOptionsLength = action.strategiesOptions.length

      const add = action.value.length > state.strategy.length

      let difference: number[] = []
      if (!add) {
        difference = state.strategy.filter((x: Strategy) => !action.value.includes(x));
      }

      return {
        ...state,
        secondModalOpen: add,
        strategy: action.value,
        dynamicStrategies: state.dynamicStrategies.reduce((accum: Strategy[], strategy: Strategy) => {
          if (action.value.includes(strategy.value) && !strategyKeys.includes(strategy.value + strategyOptionsLength)) {

            const index = strategy.value === strategyOptionsLength ?
              strategy.value : strategy.value % strategyOptionsLength

            return [...accum, strategy, {
              ...action.strategiesOptions[index - 1],
              key: strategy.value + strategyOptionsLength,
              value: strategy.value + strategyOptionsLength,
              selectedParams: {}
            }]
          } else if (difference.includes(strategy.value)) {
            return accum
          } else {
            return [...accum, strategy]
          }
        }, [])
      }
    case UPDATE_SECOND_MODAL_OPEN:
      return {
        ...state,
        secondModalOpen: action.value,
      }
    case RESET_MODAL:
      return getInitialState(action.strategiesOptions)
    case UPDATE_PARAMS:
      return {
        ...state,
        ...action.value
      }
    case UPDATE_STRATEGY_PARAMS:
      return {
        ...state,
        dynamicStrategies: state.dynamicStrategies.reduce((accum: Strategy[], strategy: Strategy) => {
          if (action.strategyIndex === strategy.value) {
            return [
              ...accum,
              {
                ...strategy,
                selectedParams: {
                  ...strategy.selectedParams,
                  ...action.value
                }
              }
            ]
          } else {
            return [...accum, strategy]
          }
        }, [])
      }
    case UPDATE_CHECKBOX:
      const liveTrading = action.value ? action.value : !state.liveTrading
      return {
        ...state,
        liveTrading,
        equity: ""
      }
    case UPDATE_STRATEGY_COMBINATION:
      return {
        ...state,
        strategyCombination: action.value,
      }
    case UPDATE_MESSAGE:
      return {
        ...state,
        message: action.message
      }
    case UPDATE_SECONDARY_MESSAGE:
      return {
        ...state,
        secondaryMessage: action.message
      }
    case GET_INITIAL_STATE:
      return {
        ...state,
        ...getInitialState(
          action.strategies,
          action.symbols,
          action.candleSizes,
          action.exchanges,
          action.pipeline
        )
      }
    default:
      throw new Error();
  }
}

export const getInitialState = (
  strategies: any,
  symbols?: any,
  candleSizes?: any,
  exchanges?: any,
  pipeline?: Pipeline
) => {
  if (pipeline) {

    const symbol = symbols.find((symbol: any) => symbol.text === pipeline.symbol)
    const candleSize = candleSizes.find((candleSize: any) => candleSize.text === pipeline.candleSize)
    const exchange = exchanges.find((exchange: any) => exchange.text === pipeline.exchange)

    const strategiesArray = pipeline.strategy.reduce(
      (strategiesArray: any, pipelineStrategy: RawStrategy) => {
        const strategy = strategies.find((strategy: Strategy) => strategy.className === pipelineStrategy.name)

        let strategyValue = strategy.value

        while (strategiesArray.includes(strategyValue)) {
          strategyValue = strategyValue + strategies.length
        }

        return [...strategiesArray, strategyValue]
    }, [])

    const strategyOptionsLength = strategies.length

    const dynamicStrategies = strategies.reduce((accum: Strategy[], strategy: Strategy) => {

      const pipelineStrategies = pipeline.strategy.filter((pipelineStrategy: RawStrategy) => pipelineStrategy.name === strategy.className)

      const extraStrategies = [
        strategy, ...pipelineStrategies.map((_, index) => {
          return {
            ...strategy,
            key: strategy.value + (index + 1) * strategyOptionsLength,
            value: strategy.value + (index + 1) * strategyOptionsLength,
          }
        })

      ].map((extraStrategy: Strategy, index: number) => {
        return {
          ...extraStrategy,
          selectedParams: index < pipelineStrategies.length ? pipelineStrategies[index].params : {}
        }
      })

      return [
        ...accum,
        ...extraStrategies
      ]
    }, [])

    return {
      strategy: strategiesArray,
      exchanges: exchange ? [exchange.value] : [],
      color: pipeline.color,
      symbol: symbol && symbol.value,
      candleSize: candleSize && candleSize.value,
      name: pipeline.name,
      equity: String(pipeline.initialEquity),
      leverage: pipeline.leverage,
      dynamicStrategies,
      liveTrading: !pipeline.paperTrading,
      strategyCombination: pipeline.strategyCombination,
      secondModalOpen: false,
      message: {text: '', success: false},
      secondaryMessage: {text: '', success: false}
    }
  } else {
    return {
      strategy: [],
      exchanges: [],
      color: null,
      symbol: null,
      candleSize: null,
      name: "",
      equity: "",
      leverage: 1,
      liveTrading: false,
      strategyCombination: 'Majority',
      secondModalOpen: false,
      dynamicStrategies: strategies.map((strategy: Strategy) => {
        return {
          ...strategy,
          selectedParams: {}
        }
      }),
      message: {text: '', success: false},
      secondaryMessage: {text: '', success: false}
    }
  }
}
