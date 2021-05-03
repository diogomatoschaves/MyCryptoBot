import StyledSegment from "../styledComponents/StyledSegment";
import {Order} from "../types";
import {Divider, Segment} from "semantic-ui-react";
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
            <Divider horizontal style={{marginBottom: '30px', marginTop: 0}}>Orders</Divider>
            {orders.map(order => {
                return <OrderCard order={order}/>
            })}
        </StyledDiv>
    );
}

export default OrdersPanel;
