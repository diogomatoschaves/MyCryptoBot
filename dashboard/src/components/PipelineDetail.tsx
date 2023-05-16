import {
  BalanceObj,
  Decimals,
  DeletePipeline, DropdownOptions, EditPipeline,
  PipelinesObject, Position,
  StartPipeline,
  StopPipeline,
  TradesMetrics, TradesObject, UpdateTrades
} from "../types";
import {Grid} from "semantic-ui-react";
import styled from "styled-components";
import TradesStats from "./TradesStats";
import TradesTable from "./TradesTable";
import PipelineItem from "./Pipeline";
import PortfolioChart from "./PortfolioChart";


const Container = styled.div`
    width: 100%;
    top: 60px;
    height: calc(100% - 50px);
    padding: 0 20px 0 30px;
    position: absolute;
`

const TradesContainer = styled(Grid.Row)`
  width: 100%;
  height: 80vh;
  padding-top: 0 !important;
  margin-top: 10px;
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
  pipelineMetrics: TradesMetrics
  startPipeline: StartPipeline
  stopPipeline: StopPipeline
  editPipeline: EditPipeline
  deletePipeline: DeletePipeline
  decimals: Decimals
  trades: TradesObject
  currentPrices: Object
  updateTrades: UpdateTrades
  symbolsOptions: DropdownOptions[];
  strategiesOptions: DropdownOptions[];
  candleSizeOptions: DropdownOptions[];
  exchangeOptions: DropdownOptions[];
  strategies: any;
  balances: BalanceObj;
  pipelinesPnl: Object
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
    pipelineMetrics,
    decimals,
    trades,
    currentPrices,
    updateTrades,
    symbolsOptions,
    strategiesOptions,
    candleSizeOptions,
    exchangeOptions,
    strategies,
    balances,
    pipelinesPnl
  } = props

  const pipeline = pipelines[pipelineId]

  return (
    <Container>
      <Grid columns={2}>
        <StatsContainer>
          <Grid.Column width={10}>
            <PipelineItem
              strategies={strategies}
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
              segmentStyle={styles.segment}
              lastRow={true}
              pipelinesPnl={pipelinesPnl}
            />
          </Grid.Column>
          <Grid.Column width={6}>
            <TradesStats tradesMetrics={pipelineMetrics} style={{height: '100%'}}/>
          </Grid.Column>
        </StatsContainer>
        <PortfolioChart pipelineId={pipelineId}/>
        <TradesContainer>
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
}
