import {Message, Table} from "semantic-ui-react";
import TradeRow from "./TradeRow";
import {Decimals, PipelinesObject, TradesObject, UpdateTrades} from "../types";
import {Wrapper} from "../styledComponents";
import {useEffect, useReducer, useRef, useState} from "react";
import {debounce, throttle} from "lodash";


interface Props {
  size: string
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
    size,
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!bottomed) return
    fetchMoreTrades(page);
    setPage(page + 1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bottomed])

  const fetchMoreTrades = (page: number) => {
    fetchData(page);
    setBottomed(false)
  };

  const fetchData = useRef(debounce(async (page: number) => {
    updateTrades(page, pipelineId)
  }, 500)).current

  const mobile = ['mobile'].includes(size)
  const cellType = mobile ? 'div' : 'th'
  const headerStyle = mobile ? styles : {}

  const tradesTableHeader = [
    <Table.HeaderCell as={cellType} style={headerStyle}>Trading Bot</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Mode</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Symbol</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Opened On</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Duration</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Side</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Units</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Leverage</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Entry Price</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Exit Price</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>PnL (ROI%)</Table.HeaderCell>
  ]

  return (
    <Wrapper maxHeight={maxHeight} onScroll={(e: any) => handleScroll(e)}>
      <Table stackable basic='very' size="small" compact striped textAlign="center">
        {!mobile && (
          <Table.Header>
            <Table.Row>
              {tradesTableHeader.map(entry => entry)}
            </Table.Row>
          </Table.Header>
        )}
        <Table.Body>
          {sortedTrades.map((tradeId: string, index: number) => {
            // @ts-ignore
            const trade = trades[tradeId]
            return (
              <TradeRow
                size={size}
                key={index}
                index={index}
                trade={trade}
                pipeline={pipelines[trade.pipelineId]}
                currentPrices={currentPrices}
                decimals={decimals}
                tradesTableHeader={tradesTableHeader}
              />
            )
          })}
        </Table.Body>
      </Table>
      {sortedTrades.length === 0 && (
          <Message>
            <Message.Header>
              No trades to show yet.
            </Message.Header>
          </Message>
      )}
      {bottomed && <h1>Fetching more list items...</h1>}
    </Wrapper>
  )
}

export default TradesTable

const styles = {
  fontWeight: '600'
}