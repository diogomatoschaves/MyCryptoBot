export const UPDATE_STRATEGY = 'UPDATE_STRATEGY'
export const UPDATE_SECOND_MODAL_OPEN = 'UPDATE_SECOND_MODAL_OPEN'
export const RESET_MODAL = 'RESET_MODAL'
export const UPDATE_STRATEGY_PARAMS = 'UPDATE_STRATEGY_PARAMS'
export const UPDATE_PARAMS = 'UPDATE_PARAMS'
export const UPDATE_CHECKBOX = 'UPDATE_CHECKBOX'
export const UPDATE_MESSAGE = 'UPDATE_MESSAGE'
export const UPDATE_SECONDARY_MESSAGE = 'UPDATE_SECONDARY_MESSAGE'


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
        allocation: "",
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
        allocation: ""
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
    default:
      throw new Error();
  }
}

export const initialState = {
  strategy: null,
  color: null,
  symbol: null,
  candleSize: null,
  name: "",
  allocation: "",
  leverage: 1,
  exchanges: [],
  liveTrading: false,
  secondModalOpen: false,
  params: {},
  message: {text: '', success: false},
  secondaryMessage: {text: '', success: false}
}