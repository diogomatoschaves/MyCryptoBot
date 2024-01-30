import {Decimals, PipelinesObject, Position} from "../types";
import {Label, Table, Image} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";
import React, {Fragment} from "react";
import {getRoi, timeFormatterDate} from "../utils/helpers";
import binanceLogo from '../utils/resources/binance.png'
import TradingBotLabel from "./TradingBotLabel";
import styled from "styled-components";


const MobileCell = styled.div`
  display: flex !important;
  flex-direction: row;
  justify-content: space-between;
  padding: 3px 0
`


interface Props {
    size: string
    index: number
    position: Position;
    pipelines: PipelinesObject
    currentPrices: Object
    decimals: Decimals
    positionsHeader: Array<any>
}

function PositionRow(props: Props) {

    const { size, position, index, currentPrices, pipelines, decimals: {quoteDecimal, baseDecimal}, positionsHeader } = props

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

    const mobile = ['mobile'].includes(size)
    const cellType = mobile ? 'div' : 'td'

    const positionsTable = [
        <Table.Cell as={cellType} style={styles.defaultCell}>
            <TradingBotLabel pipelineId={position.pipelineId} name={position.pipelineName} color={pipelineColor}/>
        </Table.Cell>,
        <Table.Cell as={cellType} style={{...styles.defaultCell, fontWeight: 600}}>
            <Label basic color='blue'>{position.paperTrading ? "test" : "live"}</Label>
        </Table.Cell>,
        <Table.Cell as={cellType} style={{fontWeight: 600, color: DARK_YELLOW}}>{position.symbol}</Table.Cell>,
        <Table.Cell as={cellType} style={styles.defaultCell}>{age}</Table.Cell>,
        <Table.Cell as={cellType} style={{color, fontWeight: '600'}}>{positionSide}</Table.Cell>,
        <Table.Cell as={cellType} style={{...styles.quantityCell, color}}>{(Number(position.amount) * markPrice).toFixed(quoteDecimal)} USDT</Table.Cell>,
        <Table.Cell as={cellType} style={styles.quantityCell}>{Number(position.amount).toFixed(baseDecimal)}</Table.Cell>,
        <Table.Cell as={cellType} style={styles.quantityCell}>{Number(position.price).toFixed(quoteDecimal)}</Table.Cell>,
        <Table.Cell as={cellType} style={styles.quantityCell}>{markPrice ? markPrice.toFixed(quoteDecimal) : '-'}</Table.Cell>,
        <Table.Cell as={cellType} style={styles.quantityCell}>{position.leverage}</Table.Cell>,
        <Table.Cell as={cellType} style={{...styles.quantityCell, color: pnlColor}}>
            {roi && `${profit.toFixed(quoteDecimal)} USDT (${roi.toFixed(2)}%)`}
        </Table.Cell>,
        <Table.Cell as={cellType} style={styles.defaultCell}>{position.exchange === 'binance' && <Image src={binanceLogo} size='tiny'/>}</Table.Cell>
    ]

    return (
      <Table.Row key={index}>
          {mobile ? (
            <Fragment>
                {positionsTable.map((entry, index) => {
                    return (
                      <MobileCell key={`trades-${index}`}>
                          {positionsHeader[index]}
                          {entry}
                      </MobileCell>
                    )})}
            </Fragment>
          ) : (
            <Fragment>
                {positionsTable.map((entry) => entry)}
            </Fragment>
          )}
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
