import {Order} from "../types";
import {Grid, Segment, Table} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED, TEAL} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";


interface Props {
    index: number
    order: Order
}

function OrdersPanel(props: Props) {

    const { order, index } = props

    const negative = order.side === 'SELL'
    const positive = order.side === 'BUY'

    const executedQty = Number(order.executedQty)
    const origQty = Number(order.origQty)
    const price = Number(order.price)
    const total = price * executedQty

    const decimalPlaces = 3

    // active={index % 2 == 0}

    return (
        <Table.Row positive={positive} negative={negative} key={index} >
            <Table.Cell style={styles.defaultCell}>{order.orderId}</Table.Cell>
            <Table.Cell style={styles.defaultCell}>{order.transactTime}</Table.Cell>
            <Table.Cell>{order.status}</Table.Cell>
            <Table.Cell style={styles.defaultCell}>{order.symbol}</Table.Cell>
            <Table.Cell>{order.side}</Table.Cell>
            <Table.Cell style={styles.defaultCell}>{executedQty.toFixed(decimalPlaces)}</Table.Cell>
            <Table.Cell style={styles.defaultCell}>{price.toFixed(decimalPlaces)}</Table.Cell>
            <Table.Cell style={styles.defaultCell}>{total.toFixed(decimalPlaces)} {order.quote}</Table.Cell>
        </Table.Row>
    );
}

export default OrdersPanel;


const styles = {
    defaultCell: {
        color: 'rgb(70, 70, 70)',
        fontWeight: '500',
    }
}
