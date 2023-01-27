import {
    BalanceObj,
    DeletePipeline,
    DropdownOptions, EditPipeline,
    Pipeline, PipelinesObject,
    Position,
    StartPipeline,
    StopPipeline,
    UpdateMessage
} from "../types";
import {Button, Grid, Icon, Label, Segment} from "semantic-ui-react";
import {BLUE, DARK_YELLOW, GREEN, RED} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";
import styled from "styled-components";
import PipelineButton from "./PipelineButton";
import {timeFormatterDate} from "../utils/helpers";
import React, {useState} from "react";
import PipelineDeleteButton from "./PipelineDeleteButton";
import NewPipeline from "./NewPipeline";


const StyledColumn = styled(Grid.Column)`
    display: flex !important;
`

const StyledRow = styled(Grid.Row)`
    padding-top: 8px !important;
    padding-bottom: 7px !important;
    & .ui.grid > .row {
        padding: 0.9rem;
    }
`

interface Props {
    pipeline: Pipeline
    startPipeline: StartPipeline
    stopPipeline: StopPipeline
    editPipeline: EditPipeline
    deletePipeline: DeletePipeline
    segmentStyle?: Object
    lastRow?: boolean
    position?: Position
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    strategies: any;
    balances: BalanceObj;
    pipelines: PipelinesObject;
    positions: Position[];
}


function PipelineItem(props: Props) {

    const {
        pipeline,
        position,
        startPipeline,
        stopPipeline,
        editPipeline,
        deletePipeline,
        segmentStyle,
        lastRow,
        symbolsOptions,
        strategiesOptions,
        candleSizeOptions,
        exchangeOptions,
        strategies,
        balances,
        positions,
        pipelines
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
            {position && (
                //@ts-ignore
                <Label size="large" attached='top right'>
                    <span
                        style={{color: position.position === -1 ? RED : position.position === 1 ? GREEN : DARK_YELLOW}}
                    >
                        {position.position === -1 ? "SHORT" : position.position === 1 ? "LONG" : "NEUTRAL"}
                    </span>
                </Label>
            )}
            <Label size="large" attached='bottom left' style={{color: BLUE}}>
                {liveStr}
            </Label>
            <Label size="large" attached='bottom right'>
                <span>
                    <span style={{color: activeProps.color, fontSize: '0.7em'}}><Icon name={'circle'}/></span>
                    <span >{activeProps.status}</span>
                </span>
            </Label>
            <Grid columns={4}>
                <StyledRow>
                    <Grid.Column width={3}>
                        <Grid.Column style={styles.header}>
                            Trading Pair
                        </Grid.Column>
                        <Grid.Column style={{...styles.rightColumn, color: DARK_YELLOW}} >
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
                            Active since
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
                            PnL {!pipeline.active && '(All time)'}
                        </Grid.Column>
                        <Grid.Column floated='right' style={{...styles.rightColumn, color}}>
                            {pnl}
                        </Grid.Column>
                    </Grid.Column>
                    <StyledColumn width={6} className="flex-row">
                        <div style={{width: '100%', alignSelf: 'center'}} className='flex-column'>
                            <NewPipeline
                              strategies={strategies}
                              balances={balances}
                              pipelines={pipelines}
                              positions={positions}
                              symbolsOptions={symbolsOptions}
                              strategiesOptions={strategiesOptions}
                              candleSizeOptions={candleSizeOptions}
                              exchangeOptions={exchangeOptions}
                              startPipeline={startPipeline}
                              editPipeline={editPipeline}
                              pipeline={pipeline}
                              edit={true}
                            >
                                <Button
                                  onClick={(event) => {
                                    event.preventDefault();
                                    event.stopPropagation()
                                  }}
                                  style={{width: '80%'}}
                                  icon
                                  disabled={pipeline.active}
                                >
                                <span style={{marginRight: '10px'}}>
                                  <Icon name={'edit'}/>
                                </span>
                                    Edit Bot
                                </Button>
                            </NewPipeline>
                        </div>
                    </StyledColumn>
                </StyledRow>
                {lastRow && (
                  <StyledRow>
                    <Grid.Column width={3}>
                        <Grid.Column floated='left' style={styles.header}>
                            Allocated Equity
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {`${pipeline.allocation} USDT`}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={4}>
                        <Grid.Column floated='left' style={styles.header}>
                            Leverage
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.leverage}
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
                          <PipelineButton
                            pipeline={pipeline}
                            startPipeline={startPipeline}
                            stopPipeline={stopPipeline}
                          />
                      </StyledColumn>
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
        padding: '55px 30px 55px',
        marginBottom: '40px',
        // border: 'none'
    },
    header: {
        color: 'rgb(130, 130, 130)',
        fontSize: '0.9em'
    },
    rightColumn: {
        fontWeight: '600',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis'
    },
}
