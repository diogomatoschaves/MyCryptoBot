import {Decimals, PipelinesObject, Position} from "../types";
import {Label, Table, Image} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";
import React from "react";
import {getRoi, timeFormatterDate} from "../utils/helpers";
import binanceLogo from '../utils/resources/binance.png'
import TradingBotLabel from "./TradingBotLabel";


interface Props {
  index: number
  position: Position;
  pipelines: PipelinesObject
  currentPrices: Object
  decimals: Decimals
}

function PositionRow(props: Props) {

    const { position, index, currentPrices, pipelines, decimals: {quoteDecimal, baseDecimal} } = props

    const negative = position.position === -1
    const positive = position.position === 1
    const positionSide = positive ? "LONG" : negative ? "SHORT" : "NEUTRAL"
    const color = negative ? RED : positive ? GREEN : DARK_YELLOW

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

    return (
      <Table.Row key={index}>
        <Table.Cell style={styles.defaultCell}>
            <TradingBotLabel pipelineId={position.pipelineId} name={position.pipelineName} color={pipelineColor}/>
        </Table.Cell>
        <Table.Cell style={{...styles.defaultCell, fontWeight: 600}}>
          <Label basic color='blue'>{position.paperTrading ? "test" : "live"}</Label>
        </Table.Cell>
        <Table.Cell style={{fontWeight: 600, color: DARK_YELLOW}}>{position.symbol}</Table.Cell>
        <Table.Cell style={styles.defaultCell}>{age}</Table.Cell>
        <Table.Cell style={{color, fontWeight: '600'}}>{positionSide}</Table.Cell>
        <Table.Cell style={{...styles.quantityCell, color}}>{(Number(position.amount) * markPrice).toFixed(quoteDecimal)} USDT</Table.Cell>
        <Table.Cell style={styles.quantityCell}>{Number(position.amount).toFixed(baseDecimal)}</Table.Cell>
        <Table.Cell style={styles.quantityCell}>{Number(position.price).toFixed(quoteDecimal)}</Table.Cell>
        <Table.Cell style={styles.quantityCell}>{markPrice ? markPrice.toFixed(quoteDecimal) : '-'}</Table.Cell>
        <Table.Cell style={styles.quantityCell}>{position.leverage}</Table.Cell>
        <Table.Cell style={{...styles.quantityCell, color: pnlColor}}>
          {roi && `${profit.toFixed(quoteDecimal)} USDT (${roi.toFixed(2)}%)`}
        </Table.Cell>
        <Table.Cell style={styles.defaultCell}>{position.exchange === 'binance' && <Image src={binanceLogo} size='tiny'/>}</Table.Cell>
      </Table.Row>
    );
}

export default PositionRow;


const styles = {
    defaultCell: {
        color: 'rgb(70, 70, 70)',
        fontWeight: '500',
    },
    quantityCell: {
        color: 'rgb(70, 70, 70)',
        fontWeight: '600',
    },
}
