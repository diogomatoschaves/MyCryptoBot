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
    height: calc(100% - 50px);
    justify-content: flex-start;
    align-items: center;
    padding-left: 30px;
    padding-top: 0;
    position: relative;
`

const FILTER_TRADES = 'FILTER_TRADES'
const TOGGLE_OPTIONS = 'TOGGLE_OPTIONS'


const reducer = (state: any, action: any) => {
    switch (action.type) {
        case FILTER_TRADES:

            const { trades, options: {test, live} } = action

            return {
                ...state,
                filteredTrades: Object.keys(trades).filter((tradeId: string) => {
                    return (trades[tradeId].mock === test && test) || (trades[tradeId].mock === !live && live)
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
        default:
            throw new Error();
    }
}


const initialOptions = {
    live: true,
    test: true
}


function TradesPanel(props: Props) {

    const { trades, pipelines, currentPrices, decimals, updateTrades } = props

    const [{filteredTrades, options}, dispatch] = useReducer(
        reducer, {
          filteredTrades: Object.keys(trades),
          options: initialOptions,
        }
    );

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

    return (
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
              updateTrades={updateTrades}
            />
      </StyledDiv>
    );
}

export default TradesPanel;
