import {MenuOption, Trade} from "../types";
import {Divider, Icon, Table} from "semantic-ui-react";
import TradeRow from './TradeRow'
import styled from "styled-components";


interface Props {
    orders: Trade[]
    menuOption: MenuOption
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

function TradesPanel(props: Props) {

    const { orders, menuOption } = props

    return (
        <StyledDiv className="flex-column">
            <Divider horizontal style={{marginBottom: '30px', marginTop: 0}}>
                <span>{menuOption.emoji}</span> {menuOption.text}
            </Divider>
            <Table basic='very'>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>start</Table.HeaderCell>
                        <Table.HeaderCell>end</Table.HeaderCell>
                        <Table.HeaderCell>symbol</Table.HeaderCell>
                        <Table.HeaderCell>type</Table.HeaderCell>
                        <Table.HeaderCell>side</Table.HeaderCell>
                        <Table.HeaderCell>quantity</Table.HeaderCell>
                        <Table.HeaderCell>price</Table.HeaderCell>
                        <Table.HeaderCell>profit/loss</Table.HeaderCell>
                        <Table.HeaderCell>exchange</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {orders.map((order, index) => {
                        return <TradeRow index={index} trade={order}/>
                    })}
                </Table.Body>
            </Table>
        </StyledDiv>
    );
}

export default TradesPanel;
