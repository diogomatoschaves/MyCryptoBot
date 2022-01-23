import {Pipeline, StartPipeline, StopPipeline} from "../types";
import { Grid, Icon, Segment} from "semantic-ui-react";
import {GREEN, RED} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";
import styled from "styled-components";
import PipelineButton from "./PipelineButton";
import {timeFormatter} from "../utils/helpers";



const PipelineDiv = styled.div`
    width: 100%;
`

const StyledColumn = styled(Grid.Column)`
    display: flex !important;
`

interface Props {
    pipeline: Pipeline
    startPipeline: StartPipeline
    stopPipeline: StopPipeline
}


function PipelineItem(props: Props) {

    const {
        pipeline,
        startPipeline,
        stopPipeline
    } = props

    const activeProps = pipeline.active ? {status: "Running", color: GREEN} : {status: "Stopped", color: RED}
    const liveStr = pipeline.paperTrading ? "Test Mode" : "Live Mode"

    const age = pipeline.openTime ? timeFormatter(pipeline.openTime) : "-"

    return (
        <PipelineDiv className="flex-row">
            <Segment style={styles.segment} secondary raised>
                <Ribbon ribbon color={'grey'}>
                    <span >
                        <span style={{color: activeProps.color, fontSize: '0.7em'}}><Icon name={'circle'}/></span>
                        <span >{activeProps.status}</span>
                        <span> | {liveStr}</span>
                    </span>
                </Ribbon>
                <Grid columns={2}>
                    <Grid.Column width={11}>
                        <Grid columns={3}>
                            <Grid.Row>
                                <Grid.Column>
                                    <Grid.Column style={styles.header}>
                                        Trading Pair
                                    </Grid.Column>
                                    <Grid.Column style={styles.rightColumn} >
                                        {pipeline.symbol}
                                    </Grid.Column>
                                </Grid.Column>
                                <Grid.Column>
                                    <Grid.Column floated='left' style={styles.header}>
                                        Strategy
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={styles.rightColumn} >
                                        {pipeline.strategy}
                                    </Grid.Column>
                                </Grid.Column>
                                <Grid.Column>
                                    <Grid.Column floated='left' style={styles.header}>
                                        Time running
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={styles.rightColumn} >
                                        {age}
                                    </Grid.Column>
                                </Grid.Column>
                            </Grid.Row>
                            <Grid.Row>
                                <Grid.Column>
                                    <Grid.Column floated='left' style={styles.header}>
                                        Candle size
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={styles.rightColumn} >
                                        {pipeline.candleSize}
                                    </Grid.Column>
                                </Grid.Column>
                                <Grid.Column>
                                    <Grid.Column floated='left' style={styles.header}>
                                        Exchange
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={styles.rightColumn} >
                                        {pipeline.exchange}
                                    </Grid.Column>
                                </Grid.Column>
                                <Grid.Column>
                                    <Grid.Column floated='left' style={styles.header}>
                                        # trades
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={styles.rightColumn} >
                                        {pipeline.numberTrades}
                                    </Grid.Column>
                                </Grid.Column>
                            </Grid.Row>
                        </Grid>
                    </Grid.Column>
                    <StyledColumn width={5} className="flex-row">
                        <div style={styles.buttonDiv} className='flex-column'>
                            <PipelineButton
                                pipeline={pipeline}
                                startPipeline={startPipeline}
                                stopPipeline={stopPipeline}
                            />
                        </div>
                    </StyledColumn>
                </Grid>
            </Segment>

        </PipelineDiv>
    );
}

export default PipelineItem;


const styles = {
    segment: {
        width: '80%',
        padding: '30px 30px 20px',
        marginBottom: '40px'
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
    buttonDiv: {
        width: '100%',
        alignSelf: 'center'
    }
}
