import {Trade} from "../types";

export const UPDATE_TRADES_STATISTICS = 'UPDATE_TRADES_STATISTICS'

export const tradesReducerCallback = (trades: Object) => (metrics: any, tradeId: string) => {

  // @ts-ignore
  const trade = trades[tradeId]

  const tradeTime = trade.closeTime.getTime() - trade.openTime.getTime()

  return {
    numberTrades: metrics.numberTrades + 1,
    maxTradeDuration: tradeTime > metrics.maxTradeDuration ? new Date(tradeTime) : metrics.maxTradeDuration,
    totalTradeDuration: metrics.totalTradeDuration + tradeTime,
    winningTrades: trade.profitLossPct && trade.profitLossPct >= 0 ? metrics.winningTrades + 1 : metrics.winningTrades,
    closedTrades: trade.profitLossPct !== null ? metrics.closedTrades + 1 : metrics.closedTrades,
    bestTrade: trade.profitLossPct && trade.profitLossPct > metrics.bestTrade
      ? trade.profitLossPct : metrics.bestTrade,
    worstTrade: trade.profitLossPct && trade.profitLossPct < metrics.worstTrade
      ? trade.profitLossPct : metrics.worstTrade
  }
}
export const tradesReducerInitialState = {
  numberTrades: 0,
  maxTradeDuration: 0,
  totalTradeDuration: 0,
  winningTrades: 0,
  closedTrades: 0,
  bestTrade: null,
  worstTrade: null
}
export const tradesReducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_TRADES_STATISTICS:
      return {
        ...state,
        ...Object.keys(action.trades).reduce(tradesReducerCallback(action.trades), tradesReducerInitialState),
      }
    default:
      throw new Error();
  }
}