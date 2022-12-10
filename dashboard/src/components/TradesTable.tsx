import {Table} from "semantic-ui-react";
import TradeRow from "./TradeRow";
import {Decimals, PipelinesObject, TradesObject, UpdateTrades} from "../types";
import {Wrapper} from "../styledComponents";
import {useEffect, useReducer, useRef, useState} from "react";
import {debounce, throttle} from "lodash";


interface Props {
  filteredTrades: string[]
  trades: TradesObject
  decimals: Decimals
  currentPrices: Object
  pipelines: PipelinesObject
  updateTrades: UpdateTrades
  maxHeight?: string
  pipelineId?: string
}

const SORT_TRADES = 'SORT_TRADES'


const reducer = (state: any, action: any) => {
  switch (action.type) {
    case SORT_TRADES:

      const { filteredTrades, trades } = action

      return {
        ...state,
        sortedTrades: filteredTrades ? filteredTrades.sort((a: string, b: string) => {
          return trades[b].closeTime.getTime() - trades[a].closeTime.getTime()
        }) : []
      }
    default:
      throw new Error();
  }
}

const TradesTable = (props: Props) => {

  const {
    filteredTrades,
    trades,
    decimals,
    currentPrices,
    pipelines,
    updateTrades,
    maxHeight,
    pipelineId
  } = props


  const [{ sortedTrades }, dispatch] = useReducer(reducer, {sortedTrades: filteredTrades})

  useEffect(() => {
    dispatch({
      type: SORT_TRADES,
      filteredTrades,
      trades
    })
  }, [filteredTrades])

  const [bottomed, setBottomed] = useState(false)
  const [page, setPage] = useState(2)

  const handleScroll = useRef(throttle((event: any) => {
    const element = event.target;
    if (Math.round(element.scrollHeight - element.scrollTop) <= element.clientHeight) {
      setBottomed(true)
    }
  }, 200)).current

  useEffect(() => {
    fetchData(1)
  }, [])

  useEffect(() => {
    if (!bottomed) return
    fetchMoreTrades(page);
    setPage(page + 1)

  }, [bottomed])

  const fetchMoreTrades = (page: number) => {
    fetchData(page);
    setBottomed(false)
  };

  const fetchData = useRef(debounce(async (page: number) => {
    updateTrades(page, pipelineId)
  }, 500)).current

  return (
    <Wrapper maxHeight={maxHeight} onScroll={(e: any) => handleScroll(e)}>
      <Table basic='very' size="small" compact striped>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell>Trading Bot</Table.HeaderCell>
            <Table.HeaderCell>Mode</Table.HeaderCell>
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
          {sortedTrades.map((tradeId: string, index: number) => {
            // @ts-ignore
            const trade = trades[tradeId]
            return (
              <TradeRow
                key={index}
                index={index}
                trade={trade}
                pipeline={pipelines[trade.pipelineId]}
                currentPrices={currentPrices}
                decimals={decimals}
              />
            )
          })}
        </Table.Body>
      </Table>
      {bottomed && <h1>Fetching more list items...</h1>}
    </Wrapper>
  )
}

export default TradesTable