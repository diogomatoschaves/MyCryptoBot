import {Decimals, Pipeline, PipelinesObject, TradesObject, UpdateTrades} from "../types";
import {Button, Header, Table} from "semantic-ui-react";
import TradeRow from './TradeRow'
import styled from "styled-components";
import {useEffect, useReducer, useRef, useState} from "react";
import {Wrapper} from "../styledComponents";
import { debounce, throttle } from 'lodash'
import TradesTable from "./TradesTable";


interface Props {
    trades: TradesObject
    pipelines: PipelinesObject
    currentPrices: Object
    decimals: Decimals
    updateTrades: UpdateTrades
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
const UPDATE_PAGE = 'UPDATE_PAGE'


const reducer = (state: any, action: any) => {
    switch (action.type) {
        case FILTER_TRADES:

            const { trades, options: {test, live} } = action

            return {
                ...state,
                filteredTrades: Object.keys(trades).filter((tradeId: string) => {
                    return (trades[tradeId].mock === test && test) || (trades[tradeId].mock === !live && live)
                }).sort((a, b) => {
                    return trades[b].closeTime.getTime() - trades[a].closeTime.getTime()
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
        case UPDATE_PAGE:
            console.log('updating page: ' + action.page)
            return {
                ...state,
                page: action.page
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

    const [bottomed, setBottomed] = useState(false)

    const { trades, pipelines, currentPrices, decimals, updateTrades } = props

    const [{filteredTrades, options, page}, dispatch] = useReducer(
        reducer, {
          filteredTrades: Object.keys(trades),
          options: initialOptions,
          page: 2
        }
    );

    const handleScroll = useRef(throttle((event: any) => {
        const element = event.target;
        if (Math.round(element.scrollHeight - element.scrollTop) <= element.clientHeight) {
            setBottomed(true)
        }
    }, 200)).current

    const previous = useRef({trades, options}).current;

    useEffect(() => {
        if (trades !== previous.trades || options !== previous.options) {
            dispatch({
                type: FILTER_TRADES,
                trades,
                options
            })
        }

        return () => {
            previous.trades = trades
            previous.options = options
        };
    }, [trades, options]);

    useEffect(() => {
        if (!bottomed) return
        fetchMoreTrades(page);
        dispatch({
            type: UPDATE_PAGE,
            page: page + 1
        })

    }, [bottomed])

    const fetchMoreTrades = (page: number) => {
        fetchData(page);
        setBottomed(false)
    };

    const fetchData = useRef(debounce(async (page: number) => {
        updateTrades(page)
    }, 500)).current

    return (
      <Wrapper onScroll={(e) => handleScroll(e)}>
        <StyledDiv className="flex-column" >
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
            <TradesTable
              filteredTrades={filteredTrades}
              trades={trades}
              decimals={decimals}
              currentPrices={currentPrices}
              pipelines={pipelines}
            />
            {bottomed && <h1>Fetching more list items...</h1>}
        </StyledDiv>
      </Wrapper>
    );
}

export default TradesPanel;
