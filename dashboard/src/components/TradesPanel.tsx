import {useEffect, useReducer, useRef} from "react";
import styled from "styled-components";
import {Decimals, PipelinesObject, TradesObject, UpdateTrades} from "../types";
import TradesTable from "./TradesTable";
import {SegmentedControl} from "../ui";


interface Props {
    size: string
    trades: TradesObject
    pipelines: PipelinesObject
    currentPrices: Object
    decimals: Decimals
    updateTrades: UpdateTrades
}


const Panel = styled.div`
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 18px;
`

const Toolbar = styled.div`
    display: flex;
    align-items: center;
    animation: fadeUp 0.3s ease both;
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

    const { size, trades, pipelines, currentPrices, decimals, updateTrades } = props

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
    }, [trades, options, previous]);

    return (
      <Panel>
          <Toolbar>
              <SegmentedControl
                options={[
                    {value: 'live', label: 'Live'},
                    {value: 'test', label: 'Test'},
                ]}
                isActive={(value) => options[value]}
                onToggle={(value) => dispatch({
                    type: TOGGLE_OPTIONS,
                    [value]: !options[value]
                })}
              />
          </Toolbar>
          <TradesTable
            size={size}
            filteredTrades={filteredTrades}
            trades={trades}
            decimals={decimals}
            currentPrices={currentPrices}
            pipelines={pipelines}
            updateTrades={updateTrades}
          />
      </Panel>
    );
}

export default TradesPanel;
