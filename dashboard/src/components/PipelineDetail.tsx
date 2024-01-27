import {
  BalanceObj,
  Decimals,
  DeletePipeline, DropdownOptions, EditPipeline,
  PipelinesObject, Position,
  StartPipeline,
  StopPipeline, Strategy,
  TradesMetrics, TradesObject, UpdateTrades
} from "../types";
import {Grid} from "semantic-ui-react";
import styled from "styled-components";
import TradesStats from "./TradesStats";
import TradesTable from "./TradesTable";
import PipelineItem from "./Pipeline";
import PortfolioChart from "./PortfolioChart";
import {useEffect, useState} from "react";
import {getTradesMetrics} from "../apiCalls";


const Container = styled.div`
    width: 100%;
    top: 60px;
    height: calc(100% - 50px);
    padding: 0 20px 0 30px;
    position: absolute;
`

const TradesContainer = styled(Grid.Row)`
  width: 100%;
  padding-top: 0 !important;
  margin-top: ${(props: any) => props.isMobile ? '20px !important' : '10px'} ;
`

const StatsContainer = styled(Grid.Row)`
  width: 100%;
  height: 30%;
  minHeight: 300px;
  position: relative;
  padding-bottom: 0 !important;
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
  }, [])

  const pipeline = pipelines[pipelineId]

  const isMobile = ['mobile'].includes(size)

  return (
    <Container>
      <Grid stackable columns={2} style={{marginTop: '20px'}}>
        <StatsContainer>
          <Grid.Column width={10}>
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
              segmentStyle={isMobile ? styles.mobileSegment : styles.segment}
              lastRow={true}
            />
          </Grid.Column>
          <Grid.Column width={6}>
            <TradesStats tradesMetrics={tradesMetrics} style={{height: '100%'}}/>
          </Grid.Column>
        </StatsContainer>
        <PortfolioChart pipelineId={pipelineId} width={'90%'}/>
        <TradesContainer isMobile={isMobile} >
          <TradesTable
            size={size}
            filteredTrades={Object.keys(trades).filter((tradeId) => trades[tradeId].pipelineId === Number(pipelineId))}
            trades={trades}
            decimals={decimals}
            currentPrices={currentPrices}
            pipelines={pipelines}
            updateTrades={updateTrades}
            maxHeight={'90%'}
            pipelineId={pipelineId}
          />
        </TradesContainer>
      </Grid>
    </Container>
  );
}


export default PipelineDetail;


const styles = {
  segment: {
    width: '100%',
    padding: '55px 30px 55px'
  },
  mobileSegment: {
    width: '100%',
    padding: '35px 20px 55px',
  },
}
