import {DeletePipeline, Pipeline, StartPipeline, StopPipeline} from "../types";
import {Button, Grid, Header, Icon, Modal, Segment} from "semantic-ui-react";
import {COLORS, GREEN, RED} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";
import styled from "styled-components";
import PipelineButton from "./PipelineButton";
import {timeFormatterDate} from "../utils/helpers";
import {useState} from "react";



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
    active: boolean
}


function PipelineItem(props: Props) {

    const {
        pipeline,
        startPipeline,
        stopPipeline,
        deletePipeline,
        active
    } = props

    const [open, setOpen] = useState(false)

    const activeProps = pipeline.active ? {status: "Running", color: GREEN} : {status: "Stopped", color: RED}
    const liveStr = pipeline.paperTrading ? "Demo" : "Live"

    const age = pipeline.openTime ? timeFormatterDate(pipeline.openTime) : "-"

    const pnl = pipeline.profitLoss ? `${(pipeline.profitLoss * 100).toFixed(2)}%` : '-'

    const color = pipeline.profitLoss > 0 ? GREEN : pipeline.profitLoss < 0 ? RED : "000000"

    return (
        <PipelineDiv className="flex-row">
            <Segment
                className={`light-${pipeline.color}`}
                style={styles.segment}
                raised
            >
                <Ribbon ribbon>
                    <span>
                        <span>{' '}{liveStr}</span>
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
                                        Time running {!active && '(All time)'}
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={styles.rightColumn} >
                                        {age}
                                    </Grid.Column>
                                </Grid.Column>
                                <StyledColumn width={6} className="flex-row">
                                    <Modal
                                        onClose={() => setOpen(false)}
                                        onOpen={() => setOpen(true)}
                                        open={open}
                                        size='small'
                                        trigger={
                                            <div style={styles.buttonDiv} className='flex-column'>
                                                <Button
                                                    icon
                                                    style={{width: '80%'}}
                                                >
                                                    <span style={{marginRight: '10px', marginLeft: '-10px'}}>
                                                        <Icon name={'delete'}/>
                                                    </span>
                                                    Delete
                                                </Button>
                                            </div>
                                        }
                                    >
                                        <Header icon>
                                            <Icon name='delete' />
                                            Delete trading bot
                                        </Header>
                                        <Modal.Content>
                                            <p>
                                                Are you sure you want to delete this trading bot?
                                            </p>
                                        </Modal.Content>
                                        <Modal.Actions>
                                            <Button
                                                color='red'
                                                inverted
                                                onClick={() => setOpen(false)}
                                            >
                                                <Icon name='remove' /> No
                                            </Button>
                                            <Button
                                                color='green'
                                                inverted
                                                onClick={() => {
                                                    deletePipeline(pipeline.id)
                                                    setOpen(false)
                                                }}
                                            >
                                                <Icon name='checkmark' /> Yes
                                            </Button>
                                        </Modal.Actions>
                                    </Modal>
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
                                        Profit / Loss {!active && '(All time)'}
                                    </Grid.Column>
                                    <Grid.Column floated='right' style={{...styles.rightColumn, color}}>
                                        {pnl}
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
                            <Grid.Row>
                                <Grid.Column width={3}>
                                    <Grid.Column floated='right' style={{...styles.rightColumn, fontSize: '1.2em'}} >
                                        <span >
                                            <span style={{color: activeProps.color, fontSize: '0.7em'}}><Icon name={'circle'}/></span>
                                            <span >{activeProps.status}</span>
                                        </span>
                                    </Grid.Column>
                                </Grid.Column>
                                <Grid.Column width={4}>
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
    buttonDiv: {
        width: '100%',
        alignSelf: 'center'
    }
}
