import {
  Decimals,
  DeletePipeline,
  Pipeline,
  PipelinesMetrics,
  PipelinesObject,
  StartPipeline,
  StopPipeline,
  TradesMetrics, TradesObject
} from "../types";
import {Button, Grid, Header, Icon, Label, Modal, Segment} from "semantic-ui-react";
import {COLORS, GREEN, RED} from "../utils/constants";
import styled from "styled-components";
import PipelineButton from "./PipelineButton";
import {timeFormatterDate} from "../utils/helpers";
import {useState} from "react";
import TradesStats from "./TradesStats";
import TradesTable from "./TradesTable";
import PipelineItem from "./Pipeline";



const PipelineDiv = styled.div`
    width: 100%;
`

const StyledColumn = styled(Grid.Column)`
    display: flex !important;
`

const StyledRow = styled(Grid.Row)`
    & .ui.grid.row {
        padding: 0.9rem;
    }
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
    currentPrices
  } = props

  const pipeline = pipelines[pipelineId]

  return (
    <PipelineDiv className="flex-row">
        <Grid columns={2}>
          <Grid.Row>
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
          </Grid.Row>
          <Grid.Row>
            <TradesTable
              filteredTrades={Object.keys(trades).filter((tradeId) => trades[tradeId].pipelineId === Number(pipelineId))}
              trades={trades}
              decimals={decimals}
              currentPrices={currentPrices}
              pipelines={pipelines}
            />
          </Grid.Row>
        </Grid>
    </PipelineDiv>
  );
}


export default PipelineDetail;


const styles = {
  segment: {
    width: '100%',
    padding: '30px 30px 20px',
  },
}
