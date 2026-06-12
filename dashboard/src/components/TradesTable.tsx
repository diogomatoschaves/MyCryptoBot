import {useEffect, useReducer, useRef, useState} from "react";
import {debounce, throttle} from "lodash";
import {ArrowLeftRight} from 'lucide-react'
import TradeRow from "./TradeRow";
import {Decimals, PipelinesObject, TradesObject, UpdateTrades} from "../types";
import {EmptyState, Spinner, Table, TableScroll} from "../ui";


const TRADES_HEADER = [
  'Trading Bot',
  'Mode',
  'Symbol',
  'Opened On',
  'Duration',
  'Side',
  'Units',
  'Leverage',
  'Entry Price',
  'Exit Price',
  'PnL (ROI%)',
]


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

  if (sortedTrades.length === 0) {
    return (
      <EmptyState
        icon={<ArrowLeftRight/>}
        title="No trades to show yet"
        hint="Closed trades will appear here as your bots operate."
      />
    )
  }

  const rows = sortedTrades.map((tradeId: string, index: number) => {
    const trade = trades[tradeId]
    return (
      <TradeRow
        size={size}
        key={tradeId}
        index={index}
        trade={trade}
        pipeline={pipelines[trade.pipelineId]}
        currentPrices={currentPrices}
        decimals={decimals}
        tradesTableHeader={TRADES_HEADER}
      />
    )
  })

  if (mobile) {
    return (
      <div
        style={{
          width: '100%',
          maxHeight: maxHeight || 'none',
          overflowY: maxHeight ? 'auto' : 'visible',
          animation: 'fadeUp 0.35s ease both',
        }}
        onScroll={(event: any) => handleScroll(event)}
      >
        {rows}
        {bottomed && (
          <div className="flex-row" style={{gap: 8, padding: 12, color: 'var(--text-faint)', fontSize: 12}}>
            <Spinner size={14}/> Loading more trades…
          </div>
        )}
      </div>
    )
  }

  return (
    <TableScroll
      $maxHeight={maxHeight || 'calc(100vh - 220px)'}
      onScroll={(event: any) => handleScroll(event)}
      style={{animation: 'fadeUp 0.35s ease both'}}
    >
      <Table>
        <thead>
          <tr>
            {TRADES_HEADER.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </Table>
      {bottomed && (
        <div className="flex-row" style={{gap: 8, padding: 12, color: 'var(--text-faint)', fontSize: 12}}>
          <Spinner size={14}/> Loading more trades…
        </div>
      )}
    </TableScroll>
  )
}

export default TradesTable
