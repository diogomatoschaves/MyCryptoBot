import {MenuOption, Pipeline, Trade} from "../types";
import {Button, Header, Table} from "semantic-ui-react";
import TradeRow from './TradeRow'
import styled from "styled-components";
import {useEffect, useReducer, useRef} from "react";


interface Props {
    trades: Trade[]
    pipelines: Pipeline[]
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
const UPDATE_PIPELINES_OBJECT = 'UPDATE_PIPELINES_OBJECT'


const reducer = (state: any, action: any) => {
    switch (action.type) {
        case FILTER_TRADES:

            const { trades, options: {test, live} } = action

            return {
                ...state,
                filteredTrades: trades.filter((trade: Trade) => {
                    return (trade.mock === test && test) || (trade.mock === !live && live)
                })
            }
        case TOGGLE_OPTIONS:
            return {
                ...state,
                options: {
                    live: action.live !== undefined ? action.live : state.options.live,
                    test: action.test !== undefined ? action.test : state.options.test,
                }
            }
        case UPDATE_PIPELINES_OBJECT:
            const {pipelines} = action
            return {
                ...state,
                pipelinesObject: pipelines.reduce((pipelinesObject: Object, pipeline: Pipeline) => {
                    return {
                        ...pipelinesObject,
                        [pipeline.id]: pipeline
                    }
                }, {})
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

    const { trades, pipelines, menuOption, currentPrices } = props

    const [{filteredTrades, options, pipelinesObject}, dispatch] = useReducer(
        reducer, {
          filteredTrades: trades,
          options: initialOptions,
          pipelinesObject: pipelines.reduce((pipelinesObject: Object, pipeline: Pipeline) => {
              return {
                  ...pipelinesObject,
                  [pipeline.id]: pipeline
              }
          }, {})
        }
    );

    const previous = useRef({trades, options, pipelines}).current;

    useEffect(() => {
        if (trades !== previous.trades || options !== previous.options) {
            dispatch({
                type: FILTER_TRADES,
                trades,
                options
            })
        }

        if (pipelines !== previous.pipelines) {
            dispatch({
                type: UPDATE_PIPELINES_OBJECT,
                pipelines
            })
        }
        return () => {
            previous.trades = trades
            previous.options = options
            previous.pipelines = pipelines
        };
    }, [trades, options, pipelines]);

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
                        <Table.HeaderCell>Mode</Table.HeaderCell>
                        <Table.HeaderCell>Trading Bot</Table.HeaderCell>
                        <Table.HeaderCell>Symbol</Table.HeaderCell>
                        <Table.HeaderCell>Opened On</Table.HeaderCell>
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
                    {filteredTrades.map((trade: Trade, index: number) => (
                      <TradeRow
                        key={index}
                        index={index}
                        trade={trade}
                        pipeline={pipelinesObject[trade.pipelineId]}
                        currentPrices={currentPrices}
                      />
                    ))}
                </Table.Body>
            </Table>
        </StyledDiv>
    );
}

export default TradesPanel;
