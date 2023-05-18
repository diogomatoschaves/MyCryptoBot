import {Fragment} from "react";
import {Decimals, Pipeline, Trade} from "../types";
import {Label, Table} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";
import {timeFormatterDate} from "../utils/helpers";
import React from "react";
import TradingBotLabel from "./TradingBotLabel";
import styled from "styled-components";


interface Props {
    size: string
    index: number
    trade: Trade,
    pipeline: Pipeline
    currentPrices: Object
    decimals: Decimals
    tradesTableHeader: Array<any>
}

const MobileCell = styled.div`
  display: flex !important;
  flex-direction: row;
  justify-content: space-between;
  padding: 3px 0
`


const dateStringOptions = {day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: 'numeric'}


function TradeRow(props: Props) {

  const { size, trade, index, decimals: {quoteDecimal, baseDecimal}, tradesTableHeader } = props

  const negative = trade.side === -1

  const side = trade.side === 1 ? "LONG" : "SHORT"

  const color = negative ? RED : GREEN

  const amount = Number(trade.amount)
  const openPrice = Number(trade.openPrice)
  const closePrice = Number(trade.closePrice)

  let profit, pnl, pnlColor
  if (trade.profitLoss !== null && trade.closePrice !== null) {
    pnlColor = trade.profitLoss > 0 ? GREEN : RED
    profit = ((trade.closePrice - trade.openPrice) * trade.amount * trade.side).toFixed(2)
    pnl = (trade.profitLoss * trade.leverage * 100).toFixed(2)
  } else {
    pnlColor = '#000000'
    profit = '-'
    pnl = '-'
  }

  const mobile = ['mobile'].includes(size)
  const cellType = mobile ? 'div' : 'td'

  const duration = timeFormatterDate(trade.openTime, trade.closeTime && trade.closeTime)
  
  const tableContent = [
    <Table.Cell as={cellType} style={styles.defaultCell}>
      <TradingBotLabel pipelineId={trade.pipelineId} name={trade.pipelineName} color={trade.pipelineColor}/>
    </Table.Cell>,
    <Table.Cell as={cellType} style={styles.defaultCell}>
      <Label basic color='blue'>{trade.mock ? "test" : "live"}</Label>
    </Table.Cell>,
    <Table.Cell as={cellType} collapsing style={{...styles.defaultCell, color: DARK_YELLOW, fontWeight: '600'}}>
      {trade.symbol}
    </Table.Cell>,
    <Table.Cell as={cellType} style={styles.defaultCell}>
      {/*@ts-ignore*/}
      {trade.openTime.toLocaleString('en-UK', dateStringOptions)}
    </Table.Cell>,
    <Table.Cell as={cellType} style={{...styles.defaultCell }}>
      {duration}
    </Table.Cell>,
    <Table.Cell as={cellType} style={{color, fontWeight: '600'}}>{side}</Table.Cell>,
    <Table.Cell as={cellType} style={{...styles.defaultCell, ...styles.quantityCell}}>
      {amount.toFixed(baseDecimal)}
    </Table.Cell>,
    <Table.Cell as={cellType} style={styles.defaultCell}>
      {trade.leverage}
    </Table.Cell>,
    <Table.Cell as={cellType} style={{...styles.defaultCell, ...styles.quantityCell}}>
      {openPrice.toFixed(quoteDecimal)}
    </Table.Cell>,
    <Table.Cell as={cellType} style={{...styles.defaultCell, ...styles.quantityCell}}>
      {closePrice.toFixed(quoteDecimal)}
    </Table.Cell>,
    <Table.Cell as={cellType} style={{...styles.defaultCell, ...styles.quantityCell, color: pnlColor}}>
      {`${profit} USDT (${pnl}%)`}
    </Table.Cell>
  ]

    return (
        <Table.Row key={index}>
          {mobile ? (
            <Fragment>
              {tableContent.map((entry, index) => {
                return (
                  <MobileCell key={`trades-${index}`}>
                    {tradesTableHeader[index]}
                    {entry}
                  </MobileCell>
              )})}
            </Fragment>
          ) : (
            <Fragment>
              {tableContent.map(entry => entry)}
            </Fragment>
          )}
        </Table.Row>
    );
}

export default TradeRow;


const styles = {
    defaultCell: {
        color: 'rgb(70, 70, 70)',
        fontWeight: '500',
    },
    mobileCell: {
      display: 'flex !important',
    },
    quantityCell: {
      // color: TEAL,
      fontWeight: '500',
    }
}
