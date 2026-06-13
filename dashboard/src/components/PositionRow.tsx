import {Fragment} from "react";
import {Decimals, PipelinesObject, Position} from "../types";
import {GREEN, RED, YELLOW, BLUE} from "../utils/constants";
import {getRoi, timeFormatterDate} from "../utils/helpers";
import TradingBotLabel from "./TradingBotLabel";
import {MobileRowCard, MobileRowLine, Num, Tag} from "../ui";
import {theme} from "../theme";


interface Props {
    size: string
    index: number
    position: Position;
    pipelines: PipelinesObject
    currentPrices: Object
    decimals: Decimals
    positionsHeader: string[]
}

function PositionRow(props: Props) {

    const { size, position, index, currentPrices, pipelines, decimals: {quoteDecimal, baseDecimal}, positionsHeader } = props

    const negative = position.position === -1
    const positive = position.position === 1
    const positionSide = positive ? "LONG" : negative ? "SHORT" : "NEUTRAL"
    const color = negative ? RED : positive ? GREEN : YELLOW

    const age = timeFormatterDate(position.openTime)

    // @ts-ignore
    const markPrice = currentPrices[position.symbol]

    // @ts-ignore
    const roi = markPrice ? getRoi(position.price, currentPrices[position.symbol], position.position, position.leverage) * 100
      : 0

    const profit = markPrice ? (markPrice - position.price) * position.amount * position.position : 0

    const pnlColor = roi > 0 ? GREEN : RED

    const pipeline = pipelines[position.pipelineId]
    const pipelineColor = pipeline && pipeline.color

    const mobile = ['mobile'].includes(size)

    const cells = [
        <TradingBotLabel pipelineId={position.pipelineId} name={position.pipelineName} color={pipelineColor}/>,
        <Tag color={position.paperTrading ? theme.blue : theme.accent}>
            {position.paperTrading ? "test" : "live"}
        </Tag>,
        <Num $color={YELLOW}>{position.symbol}</Num>,
        <span style={{color: 'var(--text-dim)'}}>{age}</span>,
        <Num $color={color}>{positionSide}</Num>,
        <Num $color={color}>{(Number(position.amount) * markPrice).toFixed(quoteDecimal)} USDT</Num>,
        <Num>{Number(position.amount).toFixed(baseDecimal)}</Num>,
        <Num>{Number(position.price).toFixed(quoteDecimal)}</Num>,
        <Num>{markPrice ? markPrice.toFixed(quoteDecimal) : '—'}</Num>,
        <Num>×{position.leverage}</Num>,
        <Num $color={pnlColor}>
            {roi ? `${profit.toFixed(quoteDecimal)} USDT (${roi.toFixed(2)}%)` : '—'}
        </Num>,
        <Num $color={BLUE} style={{textTransform: 'uppercase', fontSize: 11, letterSpacing: '0.08em'}}>
            {position.exchange}
        </Num>,
    ]

    if (mobile) {
        return (
          <MobileRowCard>
              {cells.map((cell, cellIndex) => (
                <MobileRowLine key={`position-${index}-${cellIndex}`}>
                    <span>{positionsHeader[cellIndex]}</span>
                    {cell}
                </MobileRowLine>
              ))}
          </MobileRowCard>
        )
    }

    return (
      <tr>
          {cells.map((cell, cellIndex) => (
            <td key={`position-${index}-${cellIndex}`}>{cell}</td>
          ))}
      </tr>
    );
}

export default PositionRow;
