import {DeletePipeline, Pipeline, StartPipeline, StopPipeline} from "../types";
import {Button, Grid, Icon, Segment} from "semantic-ui-react";
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
    deletePipeline: DeletePipeline
    live: boolean
}


function PipelineItem(props: Props) {

    const {
        pipeline,
        startPipeline,
        stopPipeline,
        deletePipeline,
    } = props

    const activeProps = pipeline.active ? {status: "Running", color: GREEN} : {status: "Stopped", color: RED}
    const liveStr = pipeline.paperTrading ? "Demo Mode" : "Live Trading"

    const age = pipeline.openTime ? timeFormatter(pipeline.openTime) : "-"

    const pnl = pipeline.profitLoss ? `${(pipeline.profitLoss * 100).toFixed(2)}%` : '-'

    const color = pipeline.profitLoss > 0 ? GREEN : pipeline.profitLoss < 0 ? RED : "000000"

    return (
        <PipelineDiv className="flex-row">
            <Segment style={styles.segment} secondary raised>
                <Ribbon ribbon color="grey">
                    <span >
                        <span style={{color: activeProps.color, fontSize: '0.7em'}}><Icon name={'circle'}/></span>
                        <span >{activeProps.status}</span>
                        <span> | {liveStr}</span>
                    </span>
                </Ribbon>
                <Grid columns={1}>
                    <Grid.Column width={16}>
                        <Grid columns={4}>
                            <Grid.Row>
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
                                        Time running
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={styles.rightColumn} >
                                        {age}
                                    </Grid.Column>
                                </Grid.Column>
                                <StyledColumn width={6} className="flex-row">
                                    <div style={styles.buttonDiv} className='flex-column'>
                                        <Button
                                            icon
                                            onClick={() => deletePipeline(pipeline.id)}
                                            style={{width: '80%'}}
                                        >
                                            <span style={{marginRight: '10px', marginLeft: '-10px'}}>
                                                <Icon name={'delete'}/>
                                            </span>
                                            Delete
                                        </Button>
                                    </div>
                                </StyledColumn>
                            </Grid.Row>
                            <Grid.Row>
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
                                        # trades
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={styles.rightColumn} >
                                        {pipeline.numberTrades}
                                    </Grid.Column>
                                </Grid.Column>
                                <StyledColumn width={6} className="flex-row">
                                    <div style={styles.buttonDiv} className='flex-column'>
                                        <PipelineButton
                                            pipeline={pipeline}
                                            startPipeline={startPipeline}
                                            stopPipeline={stopPipeline}
                                        />
                                    </div>
                                </StyledColumn>
                            </Grid.Row>
                        </Grid>
                    </Grid.Column>
                </Grid>
            </Segment>
        </PipelineDiv>
    );
}

// <Grid columns={1}>
//     <Grid.Column>
//         <Grid.Column floated='left' style={styles.header}>
//             Profit / Loss
//         </Grid.Column>
//         <Grid.Column floated='right' style={{...styles.rightColumn, color}}>
//             {pnl}
//         </Grid.Column>
//     </Grid.Column>
// </Grid>

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
