import {Table} from "semantic-ui-react";
import TradeRow from "./TradeRow";
import {Decimals, Pipeline, Trade, TradesObject} from "../types";


interface PipelinesObject {
  [key: string]: Pipeline
}


interface Props {
  filteredTrades: string[]
  trades: TradesObject
  decimals: Decimals
  currentPrices: Object
  pipelines: PipelinesObject
}

const TradesTable = (props: Props) => {

  const { filteredTrades, trades, decimals, currentPrices, pipelines } = props

  return (
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
  )
}

export default TradesTable