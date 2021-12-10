import {ActivePipeline, Pipeline, StartPipeline, StopPipeline} from "../types";
import {Button, Grid, Segment} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";
import styled from "styled-components";
import {stopBot} from "../apiCalls";
import PipelineButton from "./PipelineButton";



const PipelineDiv = styled.div`
    width: 100%;
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
    const liveStr = pipeline.paperTrading ? "Paper Trading" : "Live"

    return (
        <PipelineDiv className="flex-row">
            <Segment style={styles.segment}>
                <Ribbon ribbon>
                    <span>
                        <span style={{color: activeProps.color}}>{activeProps.status}</span>
                        <span> | </span>
                        <span>{liveStr}</span>
                    </span>
                </Ribbon>
                <Grid columns={2}>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Trading Pair
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.symbol}
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Strategy
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.strategy}
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Parameters
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {JSON.stringify(JSON.parse(pipeline.params))}
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Candle size
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.candleSize}
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Exchange
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.exchange}
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
            <div style={styles.buttonDiv} className='flex-column'>
                <PipelineButton
                    pipeline={pipeline}
                    startPipeline={startPipeline}
                    stopPipeline={stopPipeline}
                />
            </div>
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
    row: {
        paddingTop: '5px',
        paddingBottom: '5px',
    },
    leftColumn: {
        color: 'rgb(130, 130, 130)',
        fontWeight: 'bold',
        textAlign: 'left'
    },
    rightColumn: {
        textAlign: 'right',
        fontWeight: '600',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis'
    },
    button: {
        width: '80%'
    },
    buttonDiv: {
        width: '20%'
    }
}
