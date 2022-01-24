import {Trade} from "../types";
import {Table} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";
import {timeFormatter} from "../utils/helpers";


interface Props {
    index: number
    trade: Trade,
    currentPrices: Object
}


const dateStringOptions = {day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: 'numeric'}


const getPnl = (original: number, current: number, side: number) => {
  return ((side * (current / original) - 1) * 100).toFixed(2)
}

function TradeRow(props: Props) {

  const { trade, index, currentPrices } = props

  const negative = trade.side === -1

  const side = trade.side === 1 ? "LONG" : "SHORT"

  const color = negative ? RED : GREEN

  const amount = Number(trade.amount)
  const price = Number(trade.openPrice)

  const pnl = trade.profitLoss ?
      (trade.profitLoss * 100).toFixed(2) :
      // @ts-ignore
      currentPrices[trade.symbol] ? getPnl(trade.openPrice, currentPrices[trade.symbol], trade.side) : 0

  const pnlColor = pnl > 0 ? GREEN : RED

  const decimalPlaces = 3

  const duration = timeFormatter(trade.openTime, trade.closeTime && trade.closeTime)

  return (
        <Table.Row active={index % 2 == 0} key={index} >
            <Table.Cell style={{...styles.defaultCell, color: DARK_YELLOW, fontWeight: '600'}}>
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
              {amount.toFixed(decimalPlaces)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {price.toFixed(decimalPlaces)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell, color: pnlColor}}>
              {pnl && `${pnl}%`}
            </Table.Cell>
            <Table.Cell style={styles.defaultCell}>{trade.exchange}</Table.Cell>
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
    }
}
