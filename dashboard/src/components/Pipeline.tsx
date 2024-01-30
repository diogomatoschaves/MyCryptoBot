import {
    BalanceObj,
    DeletePipeline,
    DropdownOptions, EditPipeline,
    Pipeline, PipelinesObject,
    Position,
    StartPipeline,
    StopPipeline, Strategy,
} from "../types";
import {Button, Grid, Icon, Label, Popup, Segment} from "semantic-ui-react";
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
    padding-left: ${(props: any) => props.padding && '0 !important'};
    padding-right: ${(props: any) => props.padding && '0 !important'}
`

const StyledRow = styled(Grid.Row)`
    padding-top: 8px !important;
    padding-bottom: 7px !important;
    & .ui.grid > .row {
        padding: 0.9rem;
    }
`

interface Props {
    size: string
    pipeline: Pipeline
    startPipeline: StartPipeline
    stopPipeline: StopPipeline
    editPipeline: EditPipeline
    deletePipeline: DeletePipeline
    segmentStyle?: Object
    lastRow?: boolean
    position?: Position
    symbolsOptions: DropdownOptions[];
    strategiesOptions: Strategy[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    balances: BalanceObj;
    pipelines: PipelinesObject;
    positions: Position[];
}


function PipelineItem(props: Props) {

    const {
        size,
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
        balances,
        positions,
        pipelines,
    } = props

    const [open, setOpen] = useState(false)

    if (!pipeline) return <div></div>

    const activeProps = pipeline.active ? {status: "Running", color: GREEN} : {status: "Stopped", color: RED}
    const liveStr = pipeline.paperTrading ? "Test" : "Live"

    const age = pipeline.openTime ? timeFormatterDate(pipeline.openTime) : "-"

    const pipelinePnl = pipeline.currentEquity - pipeline.initialEquity
    const pipelinePnlPct = pipelinePnl / pipeline.initialEquity * 100

    const color = pipelinePnl > 0 ? GREEN : pipelinePnl < 0 ? RED : "000000"

    const isMobile = ['mobile'].includes(size)

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
                    <Grid.Column width={isMobile ? 5 : 3}>
                        <Grid.Column style={styles.header}>
                            Trading Pair
                        </Grid.Column>
                        <Grid.Column style={{...styles.rightColumn, color: DARK_YELLOW}} >
                            {pipeline.symbol}
                        </Grid.Column>
                    </Grid.Column>
                    <Popup
                      floated='right'
                      textAlign='right'
                      position={'top center'}
                      pinned
                      size={'large'}
                      content={
                          <div>
                              {pipeline.strategy.map((strategy, index) => {

                                  const params = Object.keys(strategy.params)

                                  return (
                                      <div>
                                          <div><span style={{fontWeight: 'bold'}}>Strategy {index + 1}:</span> {strategy.name}</div>
                                          {params.map((param, paramsIndex) => {
                                              // @ts-ignore
                                              return (
                                                  <div>
                                                      {/*@ts-ignore*/}
                                                      <span style={{fontWeight: 'bold'}}>{param}:</span> {strategy.params[param]}
                                                      {paramsIndex + 1 !== params.length && <span> — </span>}
                                                  </div>
                                              )
                                          })}
                                          {index + 1 !== pipeline.strategy.length && <br/>}
                                      </div>
                                  )
                              })}
                            </div>
                      }
                      trigger={
                          <Grid.Column width={isMobile ? 6 : 4}>
                              <Grid.Column floated='left' style={styles.header}>
                                  Strategy
                              </Grid.Column>
                              <Grid.Column floated='right' style={styles.rightColumn}>
                                  {pipeline.strategy.length > 1 ? (
                                    <div style={{fontStyle: 'italic'}}>Combined Strategy</div>
                                  ) : pipeline.strategy.length > 0 && (
                                    <div>{pipeline.strategy[0].name}</div>
                                  )}
                              </Grid.Column>
                          </Grid.Column>
                      }
                    />
                    <Grid.Column width={isMobile ? 5 : 3}>
                        <Grid.Column only={'wee'} floated='left' style={styles.header}>
                            Active since
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {age}
                        </Grid.Column>
                    </Grid.Column>
                    {!isMobile && (
                      <StyledColumn width={isMobile ? 8 : 6} className="flex-row">
                          <PipelineDeleteButton
                            pipeline={pipeline}
                            deletePipeline={deletePipeline}
                            stopPipeline={stopPipeline}
                            open={open}
                            setOpen={setOpen}
                          />
                      </StyledColumn>
                    )}
                </StyledRow>
                <StyledRow>
                    <Grid.Column width={isMobile ? 5 : 3}>
                        <Grid.Column floated='left' style={styles.header}>
                            Candle size
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.candleSize}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={isMobile ? 6 : 4}>
                        <Grid.Column floated='left' style={styles.header}>
                            Exchange
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.exchange}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={isMobile ? 5 : 3}>
                        <Grid.Column floated='left' style={styles.header}>
                            PnL (ROI%)
                        </Grid.Column>
                        <Grid.Column floated='right' style={{...styles.rightColumn, color}}>
                            {`${pipelinePnl.toFixed(2)} USDT`}<br/>
                            ({pipelinePnlPct.toFixed(2)}%)
                        </Grid.Column>
                    </Grid.Column>
                    {!isMobile && (
                        <StyledColumn width={6} className="flex-row">
                            <div style={{width: '100%', alignSelf: 'center'}} className='flex-column'>
                                <NewPipeline
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
                                  isMobile={isMobile}
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
                    )}
                </StyledRow>
                {lastRow && (
                  <StyledRow>
                    <Grid.Column width={isMobile ? 5 : 3}>
                        <Grid.Column floated='left' style={styles.header}>
                            Allocated Equity
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {`${pipeline.initialEquity} USDT`}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={isMobile ? 6 : 4}>
                        <Grid.Column floated='left' style={styles.header}>
                            Leverage
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.leverage}
                        </Grid.Column>
                    </Grid.Column>
                    <Grid.Column width={isMobile ? 5 : 3}>
                        <Grid.Column floated='left' style={styles.header}>
                            # trades
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {pipeline.numberTrades}
                        </Grid.Column>
                    </Grid.Column>
                      {!isMobile && (
                        <StyledColumn width={6} className="flex-row">
                            <PipelineButton
                              pipeline={pipeline}
                              startPipeline={startPipeline}
                              stopPipeline={stopPipeline}
                            />
                        </StyledColumn>
                      )}
                  </StyledRow>
                )}
                {isMobile && (
                  <StyledRow columns={3}>
                      <StyledColumn padding={isMobile} width={5} className="flex-row">
                          <PipelineDeleteButton
                            pipeline={pipeline}
                            deletePipeline={deletePipeline}
                            stopPipeline={stopPipeline}
                            open={open}
                            setOpen={setOpen}
                          />
                      </StyledColumn>
                      <StyledColumn padding={isMobile} width={6} className="flex-row">
                          <div style={{width: '100%', alignSelf: 'center'}} className='flex-column'>
                              <NewPipeline
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
                                isMobile={isMobile}
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
                      <StyledColumn padding={isMobile} width={5} className="flex-row">
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
    },
    mobileSegment: {
        width: '100%',
        padding: '35px 20px 55px',
        marginBottom: '40px',
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
