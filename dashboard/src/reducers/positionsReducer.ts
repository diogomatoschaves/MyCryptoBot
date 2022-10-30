import {Position} from "../types";


export const UPDATE_POSITIONS_STATISTICS = 'UPDATE_POSITIONS_STATISTICS'

export const positionsReducerCallback = (currentPrices: Object) => (metrics: any, position: Position) => {
  return {
    openPositions: metrics.openPositions + 1,
    // @ts-ignore
    totalEquityPositions: metrics.totalEquityPositions + position.amount * currentPrices[position.symbol],
    totalInitialEquity: metrics.totalEquityPositions + position.amount * position.price,
    symbolsCount: {
      ...metrics.symbolsCount,
      [position.symbol]: metrics.symbolsCount[position.symbol] ? metrics.symbolsCount[position.symbol] + 1 : 1
    }
  }
}

export const positionsReducerInitialState = {
  openPositions: 0,
  totalEquityPositions: 0,
  totalInitialEquity: 0,
  symbolsCount: {},
}

export const positionsReducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_POSITIONS_STATISTICS:
      return {
        ...state,
        ...action.positions.reduce(positionsReducerCallback(action.currentPrices), positionsReducerInitialState),
      }
    default:
      throw new Error();
  }
}