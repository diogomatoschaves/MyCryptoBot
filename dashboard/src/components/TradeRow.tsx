import {Decimals, Pipeline, Trade} from "../types";
import {Label, Table} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";
import {getRoi, timeFormatterDate} from "../utils/helpers";
import React from "react";


interface Props {
    index: number
    trade: Trade,
    pipeline: Pipeline
    currentPrices: Object
    decimals: Decimals
}


const dateStringOptions = {day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: 'numeric'}


function TradeRow(props: Props) {

  const { trade, index, decimals: {quoteDecimal, baseDecimal} } = props

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

  const duration = timeFormatterDate(trade.openTime, trade.closeTime && trade.closeTime)

    return (
        <Table.Row key={index} >
            <Table.Cell style={styles.defaultCell}>
                {/*@ts-ignore*/}
              <Label color={trade.pipelineColor as any}><span style={styles.ribbon}>{trade.pipelineName}</span></Label>
            </Table.Cell>
            <Table.Cell style={styles.defaultCell}>
                <Label basic color='blue'>{trade.mock ? "test" : "live"}</Label>
            </Table.Cell>
            <Table.Cell collapsing style={{...styles.defaultCell, color: DARK_YELLOW, fontWeight: '600'}}>
              {trade.symbol}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell}}>
              {/*@ts-ignore*/}
              {trade.openTime.toLocaleString('en-UK', dateStringOptions)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell }}>
              {duration}
            </Table.Cell>
            <Table.Cell style={{color, fontWeight: '600'}}>{side}</Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {amount.toFixed(baseDecimal)}
            </Table.Cell>
            <Table.Cell style={styles.defaultCell}>
              {trade.leverage}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {openPrice.toFixed(quoteDecimal)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {closePrice.toFixed(quoteDecimal)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell, color: pnlColor}}>
              {`${profit} USDT (${pnl}%)`}
            </Table.Cell>
        </Table.Row>
    );
}

export default TradeRow;


const styles = {
    defaultCell: {
        color: 'rgb(70, 70, 70)',
        fontWeight: '500',
    },
    quantityCell: {
      // color: TEAL,
      fontWeight: '500',
    },
    ribbon: {
        display: 'inline-block',
        maxWidth: '80px',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
    }
}
