import {Order} from "../types";
import {Label, Table} from "semantic-ui-react";
import {BLUE, DARK_YELLOW, GREEN, PURPLE, RED, TEAL, YELLOW} from "../utils/constants";


interface Props {
    index: number
    order: Order
}

function OrdersPanel(props: Props) {

  const { order, index } = props

  const negative = order.side === 'SELL'
  const positive = order.side === 'BUY'

  const color = negative ? RED : GREEN

  const executedQty = Number(order.executedQty)
  const origQty = Number(order.origQty)
  const price = Number(order.price)
  const total = price * executedQty

  const decimalPlaces = 3

    // active={index % 2 == 0}
  // positive={positive} negative={negative}

  return (
        <Table.Row active={index % 2 == 0} key={index} >
            <Table.Cell style={styles.defaultCell}>{order.orderId}</Table.Cell>
          <Table.Cell style={styles.defaultCell}>{order.transactTime.toUTCString()}</Table.Cell>
            <Table.Cell>{order.status}</Table.Cell>
            <Table.Cell style={{...styles.defaultCell, color: DARK_YELLOW}}>{order.symbol}</Table.Cell>
            <Table.Cell style={{color, fontWeight: '600'}}>{order.side}</Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {executedQty.toFixed(decimalPlaces)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {price.toFixed(decimalPlaces)}
            </Table.Cell>
            <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell}}>
              {total.toFixed(decimalPlaces)} {order.quote}
            </Table.Cell>
        </Table.Row>
    );
}

export default OrdersPanel;


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
