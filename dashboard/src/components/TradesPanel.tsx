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
const TOGGLE_OPTIONS = 'TOGGLE_OPTIONS'


const reducer = (state: any, action: any) => {
    switch (action.type) {
        case FILTER_TRADES:
            return {
                ...state,
                liveTrades: action.trades.filter((trade: Trade) => !trade.mock),
                testTrades: action.trades.filter((trade: Trade) => trade.mock),
            }
        case TOGGLE_OPTIONS:
            console.log(action)
            return {
                ...state,
                options: {
                    live: action.live !== undefined ? action.live : state.options.live,
                    test: action.test !== undefined ? action.test : state.options.test,
                }
            }
        default:
            throw new Error();
    }
}


const initialOptions = {
    live: true,
    test: true
}


function TradesPanel(props: Props) {

    const { trades, menuOption, currentPrices } = props

    const previous = useRef({trades}).current;

    const [{liveTrades, testTrades, options}, dispatch] = useReducer(
        reducer, {
          liveTrades: trades.filter((trade: Trade) => !trade.mock),
          testTrades: trades.filter((trade: Trade) => trade.mock),
          options: initialOptions
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
                {Object.keys(initialOptions).map(option =>
                    <Button onClick={() => dispatch({
                        type: TOGGLE_OPTIONS,
                        [option]: !options[option]
                    })} color={options && options[option] && 'grey'}>
                        {option}
                    </Button>
                )}
            </Button.Group>
            <Table basic='very' size="small" compact striped>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>Type </Table.HeaderCell>
                        <Table.HeaderCell>Symbol</Table.HeaderCell>
                        <Table.HeaderCell>Opened</Table.HeaderCell>
                        <Table.HeaderCell>Duration</Table.HeaderCell>
                        <Table.HeaderCell>Side</Table.HeaderCell>
                        <Table.HeaderCell>Amount</Table.HeaderCell>
                        <Table.HeaderCell>Leverage</Table.HeaderCell>
                        <Table.HeaderCell>Entry Price</Table.HeaderCell>
                        <Table.HeaderCell>Exit Price</Table.HeaderCell>
                        <Table.HeaderCell>Net Profit</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {options.live && options.test ? (
                        trades.map((trade: Trade, index: number) => {
                            return <TradeRow index={index} trade={trade} currentPrices={currentPrices}/>
                        })
                    ) : options.live ? (
                        liveTrades.map((trade: Trade, index: number) => {
                            return <TradeRow index={index} trade={trade} currentPrices={currentPrices}/>
                        })
                    ) : options.test ? (
                        testTrades.map((trade: Trade, index: number) => {
                            return <TradeRow index={index} trade={trade} currentPrices={currentPrices}/>
                        })
                    ) : (<div/>)}
                </Table.Body>
            </Table>
        </StyledDiv>
    );
}

export default TradesPanel;
