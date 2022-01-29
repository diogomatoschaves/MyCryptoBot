import {MenuOption, Trade} from "../types";
import {Button, Divider, Header, Icon, Table} from "semantic-ui-react";
import TradeRow from './TradeRow'
import styled from "styled-components";
import {useEffect, useReducer, useRef, useState} from "react";


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

const FILTER_TRADES = 'FILTER_TRADES'


const reducer = (state: any, action: any) => {
    switch (action.type) {
        case FILTER_TRADES:
            return {
                ...state,
                openTrades: action.trades.filter((trade: Trade) => !trade.closeTime),
                closedTrades: action.trades.filter((trade: Trade) => trade.closeTime),
            }
        default:
            throw new Error();
    }
}

function TradesPanel(props: Props) {

    const { trades, menuOption, currentPrices } = props

    const previous = useRef({trades}).current;

    const [open, setOpenOrClosed] = useState(true)

    const [{openTrades, closedTrades}, dispatch] = useReducer(
        reducer, {
            openTrades: trades.filter((trade: Trade) => !trade.closeTime),
            closedTrades: trades.filter((trade: Trade) => trade.closeTime),
        }
    );

    useEffect(() => {
        if (trades !== previous.trades) {
            dispatch({
                type: FILTER_TRADES,
                trades
            })
        }
        return () => {
            previous.trades = trades
        };
    }, [trades]);

    return (
        <StyledDiv className="flex-column">
            <Header size={'large'} dividing>
                <span style={{marginRight: 10}}>{menuOption.emoji}</span>
                {menuOption.text}
            </Header>
            <Button.Group size="mini" style={{alignSelf: 'center'}}>
                <Button onClick={() => setOpenOrClosed(true)} secondary={open}>Open</Button>
                <Button onClick={() => setOpenOrClosed(false)} secondary={!open}>Closed</Button>
            </Button.Group>
            <Table basic='very' size="small" compact definition >
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>Asset</Table.HeaderCell>
                        <Table.HeaderCell>Opened</Table.HeaderCell>
                        <Table.HeaderCell>Duration</Table.HeaderCell>
                        <Table.HeaderCell>Side</Table.HeaderCell>
                        <Table.HeaderCell>Amount</Table.HeaderCell>
                        <Table.HeaderCell>Buying Price</Table.HeaderCell>
                        <Table.HeaderCell>Net Profit</Table.HeaderCell>
                        <Table.HeaderCell>Exchange</Table.HeaderCell>
                        <Table.HeaderCell>Paper Trading</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {open ? (
                        openTrades.map((trade: Trade, index: number) => {
                            return <TradeRow index={index} trade={trade} currentPrices={currentPrices}/>
                        })
                    ) : (
                        closedTrades.map((trade: Trade, index: number) => {
                            return <TradeRow index={index} trade={trade} currentPrices={currentPrices}/>
                        })
                    )}
                </Table.Body>
            </Table>
        </StyledDiv>
    );
}

export default TradesPanel;
