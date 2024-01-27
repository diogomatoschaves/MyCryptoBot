import {Position} from "../types";

export const UPDATE_BALANCE = "UPDATE_BALANCE"

export const availableBalanceReducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_BALANCE:
      return {
        ...state,
        ...action.positions.reduce((accum: any, position: Position) => {
          if (position.position === 0) {
            const pipeline = action.pipelines[position.pipelineId]

            if (!pipeline) return accum

            const pipelineType = pipeline.paperTrading ? "test" : "live"
            return {
              ...accum,
              [pipelineType]: accum[pipelineType] - (pipeline.currentEquity)
            }
          } else {
            return accum
          }
        }, {
          live: action.balances.live.USDT.availableBalance,
          test: action.balances.test.USDT.availableBalance
        }),
      }
    default:

  }
}