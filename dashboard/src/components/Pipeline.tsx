import {DeletePipeline, Pipeline, StartPipeline, StopPipeline} from "../types";
import {Button, Grid, Header, Icon, Label, Modal, Segment} from "semantic-ui-react";
import {GREEN, RED} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";
import styled from "styled-components";
import PipelineButton from "./PipelineButton";
import {timeFormatterDate} from "../utils/helpers";
import {useState} from "react";
import PipelineDeleteButton from "./PipelineDeleteButton";


const StyledColumn = styled(Grid.Column)`
    display: flex !important;
`

const StyledRow = styled(Grid.Row)`
    & .ui.grid.row {
        padding: 0.9rem;
    }
`

interface Props {
    pipeline: Pipeline
    startPipeline: StartPipeline
    stopPipeline: StopPipeline
    deletePipeline: DeletePipeline
    segmentStyle?: Object
    lastRow?: boolean
}


function PipelineItem(props: Props) {

    const {
        pipeline,
        startPipeline,
        stopPipeline,
        deletePipeline,
        segmentStyle,
        lastRow
    } = props

    const [open, setOpen] = useState(false)

    if (!pipeline) return <div></div>

    const activeProps = pipeline.active ? {status: "Running", color: GREEN} : {status: "Stopped", color: RED}
    const liveStr = pipeline.paperTrading ? "Test" : "Live"

    const age = pipeline.openTime ? timeFormatterDate(pipeline.openTime) : "-"

    const pnl = pipeline.profitLoss ? `${(pipeline.profitLoss * 100).toFixed(2)}%` : '-'

    const color = pipeline.profitLoss > 0 ? GREEN : pipeline.profitLoss < 0 ? RED : "000000"

    return (
        <Segment
            secondary
            style={segmentStyle ? segmentStyle : styles.segment}
            raised
        >
            <Ribbon color={pipeline.color} ribbon>
                {pipeline.name}
            </Ribbon>
            <Grid columns={4}>
                <StyledRow>
                    <Grid.Column width={3}>
                        <Grid.Column style={styles.header}>
                            Trading Pair
                        </Grid.Column>
                        <Grid.Column style={styles.rightColumn} >
                            {pipeline.symbol}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={4}>
                        <Grid.Column floated='left' style={styles.header}>
                            Strategy
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.strategy}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={3}>
                        <Grid.Column floated='left' style={styles.header}>
                            Time running {!pipeline.active && '(All time)'}
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {age}
                        </Grid.Column>
                    </Grid.Column>
                    <StyledColumn width={6} className="flex-row">
                        <PipelineDeleteButton
                            pipeline={pipeline}
                            deletePipeline={deletePipeline}
                            stopPipeline={stopPipeline}
                            open={open}
                            setOpen={setOpen}
                        />
                    </StyledColumn>
                </StyledRow>
                <StyledRow>
                    <Grid.Column width={3}>
                        <Grid.Column floated='left' style={styles.header}>
                            Candle size
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.candleSize}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={4}>
                        <Grid.Column floated='left' style={styles.header}>
                            Exchange
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.exchange}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={3}>
                        <Grid.Column floated='left' style={styles.header}>
                            Profit / Loss {!pipeline.active && '(All time)'}
                        </Grid.Column>
                        <Grid.Column floated='right' style={{...styles.rightColumn, color}}>
                            {pnl}
                        </Grid.Column>
                    </Grid.Column>
                    <StyledColumn width={6} className="flex-row">
                        <PipelineButton
                            pipeline={pipeline}
                            startPipeline={startPipeline}
                            stopPipeline={stopPipeline}
                        />
                    </StyledColumn>
                </StyledRow>
                {lastRow && (
                  <StyledRow>
                    <Grid.Column width={3}>
                        <Grid.Column floated='right' style={{...styles.rightColumn, fontSize: '1.2em'}} >
                            <span >
                                <span style={{color: activeProps.color, fontSize: '0.7em'}}><Icon name={'circle'}/></span>
                                <span >{activeProps.status}</span>
                            </span>
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={4}>
                        <Grid.Column floated='right' style={{...styles.rightColumn, fontSize: '1.2em'}} >
                            <Label color='blue' basic>{liveStr}</Label>
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={3}>
                        <Grid.Column floated='left' style={styles.header}>
                            # trades
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.numberTrades}
                        </Grid.Column>
                    </Grid.Column>
                  </StyledRow>
                )}
            </Grid>
        </Segment>
    );
}


export default PipelineItem;


const styles = {
    segment: {
        width: '100%',
        padding: '30px 30px 20px',
        marginBottom: '40px',
        // border: 'none'
    },
    header: {
        color: 'rgb(130, 130, 130)',
    },
    rightColumn: {
        fontWeight: '600',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis'
    },
}
