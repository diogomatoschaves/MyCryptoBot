import {MenuOption, Trade} from "../types";
import {Divider, Icon, Table} from "semantic-ui-react";
import TradeRow from './TradeRow'
import styled from "styled-components";


interface Props {
    trades: Trade[]
    menuOption: MenuOption
    currentPrices: Object
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

    const { trades, menuOption, currentPrices } = props

    return (
        <StyledDiv className="flex-column">
            <Divider horizontal style={{marginBottom: '30px', marginTop: 0}}>
                <span>{menuOption.emoji}</span> {menuOption.text}
            </Divider>
            <Table basic='very'>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>Asset</Table.HeaderCell>
                        <Table.HeaderCell>Open</Table.HeaderCell>
                        <Table.HeaderCell>Duration</Table.HeaderCell>
                        <Table.HeaderCell>Side</Table.HeaderCell>
                        <Table.HeaderCell>Amount</Table.HeaderCell>
                        <Table.HeaderCell>Price</Table.HeaderCell>
                        <Table.HeaderCell>Net Profit</Table.HeaderCell>
                        <Table.HeaderCell>Exchange</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {trades.map((trade, index) => {
                        return <TradeRow index={index} trade={trade} currentPrices={currentPrices}/>
                    })}
                </Table.Body>
            </Table>
        </StyledDiv>
    );
}

export default TradesPanel;
