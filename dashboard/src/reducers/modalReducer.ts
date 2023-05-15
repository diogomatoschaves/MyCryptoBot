import {Pipeline} from "../types";

export const UPDATE_STRATEGY = 'UPDATE_STRATEGY'
export const UPDATE_SECOND_MODAL_OPEN = 'UPDATE_SECOND_MODAL_OPEN'
export const RESET_MODAL = 'RESET_MODAL'
export const UPDATE_STRATEGY_PARAMS = 'UPDATE_STRATEGY_PARAMS'
export const UPDATE_PARAMS = 'UPDATE_PARAMS'
export const UPDATE_CHECKBOX = 'UPDATE_CHECKBOX'
export const UPDATE_MESSAGE = 'UPDATE_MESSAGE'
export const UPDATE_SECONDARY_MESSAGE = 'UPDATE_SECONDARY_MESSAGE'
export const GET_INITIAL_STATE = 'GET_INITIAL_STATE'


export const modalReducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_STRATEGY:
      return {
        ...state,
        secondModalOpen: action.value !== null,
        strategy: action.value,
        params: action.value === null ? {} : state.params
      }
    case UPDATE_SECOND_MODAL_OPEN:
      return {
        ...state,
        secondModalOpen: action.value,
      }
    case RESET_MODAL:
      return {
        ...state,
        strategy: null,
        color: null,
        symbol: null,
        candleSize: null,
        name: "",
        equity: "",
        leverage: 1,
        exchanges: [],
        liveTrading: false,
        secondModalOpen: false,
        params: {},
        message: {text: '', success: false},
        secondaryMessage: {text: '', success: false},
      }
    case UPDATE_PARAMS:
      return {
        ...state,
        ...action.value
      }
    case UPDATE_STRATEGY_PARAMS:
      return {
        ...state,
        params: {
          ...state.params,
          ...action.value
        },
      }
    case UPDATE_CHECKBOX:
      const liveTrading = action.value ? action.value : !state.liveTrading
      return {
        ...state,
        liveTrading,
        equity: ""
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
          action.symbols,
          action.strategies,
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
  symbols: any,
  strategies: any,
  candleSizes: any,
  exchanges: any,
  pipeline?: Pipeline
) => {
  if (pipeline) {
    const strategy = strategies.find((strategy: any) => strategy.text === pipeline.strategy)
    const symbol = symbols.find((symbol: any) => symbol.text === pipeline.symbol)
    const candleSize = candleSizes.find((candleSize: any) => candleSize.text === pipeline.candleSize)
    const exchange = exchanges.find((exchange: any) => exchange.text === pipeline.exchange)

    return {
      strategy: strategy && strategy.value,
      color: pipeline.color,
      symbol: symbol && symbol.value,
      candleSize: candleSize && candleSize.value,
      name: pipeline.name,
      equity: String(pipeline.equity),
      leverage: pipeline.leverage,
      exchanges: exchange && [exchange.value],
      params: pipeline.params,
      liveTrading: !pipeline.paperTrading,
      secondModalOpen: false,
      message: {text: '', success: false},
      secondaryMessage: {text: '', success: false}
    }
  } else {
    return {
      strategy: null,
      color: null,
      symbol: null,
      candleSize: null,
      name: "",
      equity: "",
      leverage: 1,
      exchanges: [],
      liveTrading: false,
      secondModalOpen: false,
      params: {},
      message: {text: '', success: false},
      secondaryMessage: {text: '', success: false}
    }
  }
}

export const initialState = {

}