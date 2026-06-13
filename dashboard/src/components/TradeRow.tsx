import {Decimals, Pipeline, Trade} from "../types";
import {GREEN, RED, YELLOW} from "../utils/constants";
import {timeFormatterDate} from "../utils/helpers";
import TradingBotLabel from "./TradingBotLabel";
import {MobileRowCard, MobileRowLine, Num, Tag} from "../ui";
import {theme} from "../theme";


interface Props {
    size: string
    index: number
    trade: Trade,
    pipeline: Pipeline
    currentPrices: Object
    decimals: Decimals
    tradesTableHeader: string[]
}


const dateStringOptions = {day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: 'numeric'}


function TradeRow(props: Props) {

  const { size, trade, index, decimals: {quoteDecimal, baseDecimal}, tradesTableHeader } = props

  const negative = trade.side === -1

  const side = trade.side === 1 ? "LONG" : "SHORT"

  const color = negative ? RED : GREEN

  const amount = Number(trade.amount)
  const openPrice = Number(trade.openPrice)
  const closePrice = Number(trade.closePrice)

  const profitLoss = trade.profitLoss ? trade.profitLoss.toFixed(2) : '—'
  const profitLossPct = trade.profitLossPct ? (trade.profitLossPct * 100).toFixed(2) : '—'
  const pnlColor = trade.profitLossPct ? trade.profitLossPct > 0 ? GREEN : RED : theme.textDim

  const mobile = ['mobile'].includes(size)

  const duration = timeFormatterDate(trade.openTime, trade.closeTime && trade.closeTime)

  const cells = [
    <TradingBotLabel pipelineId={trade.pipelineId} name={trade.pipelineName} color={trade.pipelineColor}/>,
    <Tag color={trade.mock ? theme.blue : theme.accent}>
      {trade.mock ? "test" : "live"}
    </Tag>,
    <Num $color={YELLOW}>{trade.symbol}</Num>,
    <span style={{color: 'var(--text-dim)'}}>
      {/*@ts-ignore*/}
      {trade.openTime.toLocaleString('en-UK', dateStringOptions)}
    </span>,
    <span style={{color: 'var(--text-dim)'}}>{duration}</span>,
    <Num $color={color}>{side}</Num>,
    <Num>{amount.toFixed(baseDecimal)}</Num>,
    <Num>×{trade.leverage}</Num>,
    <Num>{openPrice.toFixed(quoteDecimal)}</Num>,
    <Num>{closePrice.toFixed(quoteDecimal)}</Num>,
    <Num $color={pnlColor}>{`${profitLoss} USDT (${profitLossPct}%)`}</Num>,
  ]

  if (mobile) {
    return (
      <MobileRowCard>
        {cells.map((cell, cellIndex) => (
          <MobileRowLine key={`trade-${index}-${cellIndex}`}>
            <span>{tradesTableHeader[cellIndex]}</span>
            {cell}
          </MobileRowLine>
        ))}
      </MobileRowCard>
    )
  }

  return (
    <tr>
      {cells.map((cell, cellIndex) => (
        <td key={`trade-${index}-${cellIndex}`}>{cell}</td>
      ))}
    </tr>
  );
}

export default TradeRow;
