import {Pipeline, Trade} from "../types";

export const UPDATE_PIPELINES_STATISTICS = 'UPDATE_PIPELINES_STATISTICS'


type TradesMetrics = {
  totalTrades: number,
  win: number
}

export const pipelinesReducerCallback = (trades: Trade[]) => (metrics: any, pipeline: Pipeline) => {

  const tradesMetrics = trades.reduce((tradesMetrics: TradesMetrics, trade: Trade) => {
    if (trade.pipelineId === pipeline.id) {
      return {
        totalTrades: tradesMetrics.totalTrades + 1,
        win: trade.profitLoss && trade.profitLoss > 0 ? tradesMetrics.win + 1 : tradesMetrics.win
      }
    }
    return tradesMetrics
  }, {totalTrades: 0, win: 0})

  const winRate = tradesMetrics.totalTrades > 0 ? tradesMetrics.win / tradesMetrics.totalTrades : 0

  return {
    totalPipelines: metrics.totalPipelines + 1,
    activePipelines: pipeline.active ? metrics.activePipelines + 1 : metrics.activePipelines,
    bestWinRate: winRate > metrics.bestWinRate.winRate ? {...pipeline, winRate} : metrics.bestWinRate,
    mostTrades: tradesMetrics.totalTrades > metrics.mostTrades.totalTrades ?
      {...pipeline, totalTrades: tradesMetrics.totalTrades} : metrics.mostTrades,
  }
}
export const pipelinesReducerInitialState = {
  totalPipelines: 0,
  activePipelines: 0,
  bestWinRate: {winRate: 0},
  mostTrades: {totalTrades: 0}
}
export const pipelinesReducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_PIPELINES_STATISTICS:
      return {
        ...state,
        ...action.pipelines.reduce(pipelinesReducerCallback(action.trades), pipelinesReducerInitialState),
      }
    default:
      throw new Error();
  }
}