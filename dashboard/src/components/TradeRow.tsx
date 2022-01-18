import {Trade} from "../types";
import {Table} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";


interface Props {
    index: number
    trade: Trade
}

function TradeRow(props: Props) {

  const { trade, index } = props

  const negative = trade.side === 'SELL'

  const color = negative ? RED : GREEN

  const amount = Number(trade.amount)
  const price = Number(trade.openPrice)
  const total = price * amount

  const pnl = `${trade.profitLoss && (trade.profitLoss * 100).toFixed(2)}%`

  const decimalPlaces = 3

  return (
        <Table.Row active={index % 2 == 0} key={index} >
            <Table.Cell style={{...styles.defaultCell, fontWeight: 600}}>
              {trade.openTime.toLocaleString()}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, fontWeight: 600}}>
              {trade.closeTime && trade.closeTime.toLocaleString()}
            </Table.Cell>
            <Table.Cell>{trade.type}</Table.Cell>
            <Table.Cell style={{...styles.defaultCell, color: DARK_YELLOW}}>{trade.symbol}</Table.Cell>
            <Table.Cell style={styles.defaultCell}>{trade.exchange}</Table.Cell>
            <Table.Cell style={{color, fontWeight: '600'}}>{trade.side}</Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {amount.toFixed(decimalPlaces)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {price.toFixed(decimalPlaces)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {pnl}
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
    }
}
