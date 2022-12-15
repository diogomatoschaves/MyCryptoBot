import {Position} from "../types";


export const UPDATE_POSITIONS_STATISTICS = 'UPDATE_POSITIONS_STATISTICS'

export const positionsReducerCallback = (currentPrices: Object) => (metrics: any, position: Position) => {

  // @ts-ignore
  const currentValue = position.amount * currentPrices[position.symbol]
  const initialValue = position.amount * position.price

  const pnl = (currentValue - initialValue) / initialValue * position.position

  return {
    openPositions: metrics.openPositions + 1,

    totalEquityPositions: metrics.totalEquityPositions + currentValue,
    totalInitialEquity: metrics.totalInitialEquity + initialValue,
    pnl: metrics.pnl + pnl * initialValue,
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
  pnl: 0,
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