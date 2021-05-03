import {Order} from "../types";
import {Grid, Label, Segment} from "semantic-ui-react";
import styled, {css} from "styled-components";
import {DARK_YELLOW, GREEN, RED, TEAL} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";


interface Props {
    order: Order
}

const separatorColor = 'rgb(180, 180, 180)'

function OrdersPanel(props: Props) {

    const { order } = props

    const sideColor = order.side === 'SELL' ? RED : GREEN

    const executedQty = Number(order.executedQty)
    const origQty = Number(order.origQty)
    const price = Number(order.price)
    const total = price * executedQty

    const decimalPlaces = 3

    return (
        <Segment style={styles.segment}>
            <Ribbon ribbon>
                <span style={{color: DARK_YELLOW}}>{order.symbol}
                    <span style={{color: separatorColor}}> | </span>
                    <span style={{color: sideColor}}> {order.side}</span>
                    <span style={{color: separatorColor}}> | </span>
                    <span style={{color: TEAL}}> {order.status}</span>
                </span>
            </Ribbon>
            <Grid columns={2}>
                <Grid.Row style={styles.row}>
                    <Grid.Column floated='left' style={styles.leftColumn}>
                        Order No.
                    </Grid.Column>
                    <Grid.Column floated='right' style={styles.rightColumn} >
                        {order.orderId}
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row style={styles.row}>
                    <Grid.Column floated='left' style={styles.leftColumn}>
                        Executed / Amount
                    </Grid.Column>
                    <Grid.Column floated='right' style={styles.rightColumn} >
                        {executedQty.toFixed(decimalPlaces)} / {origQty.toFixed(decimalPlaces)}
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row style={styles.row}>
                    <Grid.Column floated='left' style={styles.leftColumn}>
                        Average Price
                    </Grid.Column>
                    <Grid.Column floated='right' style={styles.rightColumn} >
                        {price.toFixed(decimalPlaces)}
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row style={styles.row}>
                    <Grid.Column floated='left' style={styles.leftColumn}>
                        Total
                    </Grid.Column>
                    <Grid.Column floated='right' style={styles.rightColumn} >
                        {total.toFixed(decimalPlaces)} {order.quote}
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </Segment>
    );
}

export default OrdersPanel;


const styles = {
    segment: {
        width: '100%',
        padding: '30px 30px 20px'
    },
    row: {
        paddingTop: '5px',
        paddingBottom: '5px',
    },
    leftColumn: {
        color: 'rgb(130, 130, 130)',
        fontWeight: 'bold',
        textAlign: 'left'
    },
    rightColumn: {
        textAlign: 'right',
        fontWeight: '600',
    }
}
