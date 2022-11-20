import {
  Decimals,
  DeletePipeline,
  PipelinesObject,
  StartPipeline,
  StopPipeline,
  TradesMetrics, TradesObject, UpdateTrades
} from "../types";
import {Grid, Icon} from "semantic-ui-react";
import styled from "styled-components";
import TradesStats from "./TradesStats";
import TradesTable from "./TradesTable";
import PipelineItem from "./Pipeline";


const Container = styled.div`
    width: 100%;
    top: 60px;
    height: calc(100% - 50px);
    position: absolute;
`

const TradesContainer = styled(Grid.Row)`
  width: 100%;
  height: 70vh;
  padding-top: 0 !important;
  margin-top: 10px;
`

const StatsContainer = styled(Grid.Row)`
  width: 100%;
  height: 30%;
  minHeight: 300px;
  position: relative;
`

interface Props {
  pipelines: PipelinesObject
  pipelineId: string
  pipelineMetrics: TradesMetrics
  startPipeline: StartPipeline
  stopPipeline: StopPipeline
  deletePipeline: DeletePipeline
  decimals: Decimals
  trades: TradesObject
  currentPrices: Object
  updateTrades: UpdateTrades
}


function PipelineDetail(props: Props) {

  const {
    pipelines,
    pipelineId,
    startPipeline,
    stopPipeline,
    deletePipeline,
    pipelineMetrics,
    decimals,
    trades,
    currentPrices,
    updateTrades
  } = props

  const pipeline = pipelines[pipelineId]

  return (
    <Container>
      <Grid columns={2}>
        <StatsContainer>
          <Grid.Column width={10}>
            <PipelineItem
              pipeline={pipeline}
              startPipeline={startPipeline}
              stopPipeline={stopPipeline}
              deletePipeline={deletePipeline}
              segmentStyle={styles.segment}
            />
          </Grid.Column>
          <Grid.Column width={6}>
            <TradesStats tradesMetrics={pipelineMetrics}/>
          </Grid.Column>
        </StatsContainer>
        <TradesContainer>
          <TradesTable
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
    padding: '30px 30px 20px',
  },
}
