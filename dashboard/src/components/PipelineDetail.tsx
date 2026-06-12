import {useEffect, useState} from "react";
import styled from "styled-components";
import {ChevronLeft, TrendingUp} from 'lucide-react'
import {Link} from 'react-router-dom'
import {
  BalanceObj,
  Decimals,
  DeletePipeline, DropdownOptions, EditPipeline,
  PipelinesObject, Position,
  StartPipeline,
  StopPipeline, Strategy,
  TradesObject, UpdateTrades
} from "../types";
import TradesStats from "./TradesStats";
import TradesTable from "./TradesTable";
import PipelineItem from "./Pipeline";
import PortfolioChart from "./PortfolioChart";
import {getTradesMetrics} from "../apiCalls";
import {Card, CardHeader, CardTitle} from "../ui";
import {getBotColor} from "../theme";


const Container = styled.div`
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 18px;
`

const BackLink = styled(Link)`
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-faint);
    transition: color 0.15s ease;
    width: fit-content;

    &:hover {
        color: var(--text);
    }

    svg {
        width: 14px;
        height: 14px;
    }
`

const TopGrid = styled.div`
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
    gap: 18px;
    align-items: start;

    @media (max-width: 991px) {
        grid-template-columns: 1fr;
    }
`

interface Props {
  size: string
  pipelines: PipelinesObject
  positions: Position[]
  pipelineId: string
  startPipeline: StartPipeline
  stopPipeline: StopPipeline
  editPipeline: EditPipeline
  deletePipeline: DeletePipeline
  decimals: Decimals
  trades: TradesObject
  currentPrices: Object
  updateTrades: UpdateTrades
  symbolsOptions: DropdownOptions[];
  strategiesOptions: Strategy[];
  candleSizeOptions: DropdownOptions[];
  exchangeOptions: DropdownOptions[];
  balances: BalanceObj;
}


function PipelineDetail(props: Props) {

  const {
    size,
    pipelines,
    positions,
    pipelineId,
    startPipeline,
    stopPipeline,
    editPipeline,
    deletePipeline,
    decimals,
    trades,
    currentPrices,
    updateTrades,
    symbolsOptions,
    strategiesOptions,
    candleSizeOptions,
    exchangeOptions,
    balances,
  } = props

  const fetchTradesData = async (pipelineId: string) => {
    const tradesMetrics = await getTradesMetrics(pipelineId)
    setTradesMetrics(tradesMetrics)
  }

  const [tradesMetrics, setTradesMetrics] = useState({
    numberTrades: 0,
    maxTradeDuration: 0,
    avgTradeDuration: 0,
    winningTrades: 0,
    losingTrades: 0,
    bestTrade: 0,
    worstTrade: 0,
    tradesCount: []
  })

  useEffect(() =>{
    fetchTradesData(pipelineId)
    .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const pipeline = pipelines[pipelineId]

  return (
    <Container>
      <BackLink to="/pipelines">
        <ChevronLeft/>
        All bots
      </BackLink>
      <TopGrid>
        <PipelineItem
          size={size}
          balances={balances}
          pipelines={pipelines}
          positions={positions}
          symbolsOptions={symbolsOptions}
          strategiesOptions={strategiesOptions}
          candleSizeOptions={candleSizeOptions}
          exchangeOptions={exchangeOptions}
          pipeline={pipeline}
          startPipeline={startPipeline}
          editPipeline={editPipeline}
          stopPipeline={stopPipeline}
          deletePipeline={deletePipeline}
          position={positions.find((position) => String(position.pipelineId) === pipelineId)}
          lastRow={true}
        />
        <TradesStats tradesMetrics={tradesMetrics}/>
      </TopGrid>
      <Card>
        <CardHeader>
          <CardTitle>
            <TrendingUp/>
            Equity
          </CardTitle>
        </CardHeader>
        <PortfolioChart
          pipelineId={pipelineId}
          height={220}
          color={pipeline ? getBotColor(pipeline.color) : undefined}
        />
      </Card>
      <TradesTable
        size={size}
        filteredTrades={Object.keys(trades).filter((tradeId) => trades[tradeId].pipelineId === Number(pipelineId))}
        trades={trades}
        decimals={decimals}
        currentPrices={currentPrices}
        pipelines={pipelines}
        updateTrades={updateTrades}
        maxHeight={'480px'}
        pipelineId={pipelineId}
      />
    </Container>
  );
}


export default PipelineDetail;
