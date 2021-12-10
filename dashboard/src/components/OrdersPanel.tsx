import {Order} from "../types";
import {Divider, Table} from "semantic-ui-react";
import OrderCard from './Order'
import styled from "styled-components";


interface Props {
    orders: Order[]
}


const StyledDiv = styled.div`
    width: 100%;
    height: 100%;
    justify-content: flex-start;
    align-items: center;
    padding: 30px;
    padding-top: 0;
    position: relative;
`

function OrdersPanel(props: Props) {

    const { orders } = props

    return (
        <StyledDiv className="flex-column">
            <Divider horizontal style={{marginBottom: '30px', marginTop: 0}}>Transactions</Divider>
            <Table basic='very'>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>Order Id</Table.HeaderCell>
                        <Table.HeaderCell>Time</Table.HeaderCell>
                        <Table.HeaderCell>Status</Table.HeaderCell>
                        <Table.HeaderCell>Trading Pair</Table.HeaderCell>
                        <Table.HeaderCell>Side</Table.HeaderCell>
                        <Table.HeaderCell>Quantity</Table.HeaderCell>
                        <Table.HeaderCell>Buying Price</Table.HeaderCell>
                        <Table.HeaderCell>Total</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {orders.map((order, index) => {
                        return <OrderCard index={index} order={order}/>
                    })}
                </Table.Body>
            </Table>
        </StyledDiv>
    );
}

export default OrdersPanel;
