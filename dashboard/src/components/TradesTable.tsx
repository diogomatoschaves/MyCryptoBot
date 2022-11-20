import {Table} from "semantic-ui-react";
import TradeRow from "./TradeRow";
import {Decimals, PipelinesObject, TradesObject, UpdateTrades} from "../types";
import {Wrapper} from "../styledComponents";
import {useEffect, useRef, useState} from "react";
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

const TradesTable = (props: Props) => {

  const { filteredTrades, trades, decimals, currentPrices, pipelines, updateTrades, maxHeight, pipelineId } = props

  console.log(pipelineId)

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
          {filteredTrades.map((tradeId: string, index: number) => {
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