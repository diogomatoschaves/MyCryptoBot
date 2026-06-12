import {useState} from "react";
import styled from "styled-components";
import {Pencil} from 'lucide-react'
import {
    BalanceObj,
    DeletePipeline,
    DropdownOptions, EditPipeline,
    Pipeline, PipelinesObject,
    Position,
    StartPipeline,
    StopPipeline, Strategy,
} from "../types";
import {GREEN, RED, YELLOW} from "../utils/constants";
import PipelineButton from "./PipelineButton";
import {timeFormatterDate} from "../utils/helpers";
import PipelineDeleteButton from "./PipelineDeleteButton";
import NewPipeline from "./NewPipeline";
import {Button, Card, Stat, Tag} from "../ui";
import {getBotColor, theme} from "../theme";


const BotCard = styled(Card)`
    display: flex;
    gap: 24px;
    width: 100%;
    margin-bottom: 16px;

    @media (max-width: 767px) {
        flex-direction: column;
    }
`

const BotInfo = styled.div`
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 18px;
`

const BotHeader = styled.div`
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
`

const BotName = styled.span<{$color: string}>`
    display: flex;
    align-items: center;
    gap: 9px;
    font-family: var(--font-ui);
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
    min-width: 0;

    &::before {
        content: '';
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
        background: ${({$color}) => $color};
        box-shadow: 0 0 10px ${({$color}) => $color};
    }

    span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
`

const StatusDot = styled.span<{$running: boolean}>`
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: ${({$running}) => ($running ? 'var(--green)' : 'var(--text-faint)')};
    box-shadow: ${({$running}) => ($running ? '0 0 8px var(--green)' : 'none')};
    animation: ${({$running}) => ($running ? 'pulseGlow 2.2s ease infinite' : 'none')};
`

const StatsGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 16px 18px;
`

const Actions = styled.div`
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 8px;
    width: 150px;
    flex-shrink: 0;

    @media (max-width: 767px) {
        flex-direction: row;
        width: 100%;

        & > * {
            flex: 1;
        }
    }
`

const StrategyHover = styled.div`
    position: relative;
    display: inline-block;

    & > div.tooltip {
        display: none;
        position: absolute;
        bottom: calc(100% + 8px);
        left: 0;
        z-index: 40;
        min-width: 220px;
        background: var(--bg-elevated);
        border: 1px solid var(--border-strong);
        border-radius: var(--radius-sm);
        box-shadow: var(--shadow-pop);
        padding: 12px 14px;
        font-size: 12px;
        font-weight: 400;
        font-family: var(--font-ui);
        color: var(--text-dim);
        white-space: normal;
        text-align: left;
    }

    &:hover > div.tooltip {
        display: block;
        animation: fadeIn 0.12s ease;
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

    const age = pipeline.openTime ? timeFormatterDate(pipeline.openTime) : "—"

    const pipelinePnl = pipeline.currentEquity - pipeline.initialEquity
    const pipelinePnlPct = pipelinePnl / pipeline.initialEquity * 100

    const pnlColor = pipelinePnl > 0 ? GREEN : pipelinePnl < 0 ? RED : theme.textDim

    const positionSide = position
      ? position.position === -1 ? "SHORT" : position.position === 1 ? "LONG" : "NEUTRAL"
      : null
    const positionColor = position
      ? position.position === -1 ? RED : position.position === 1 ? GREEN : YELLOW
      : undefined

    const isMobile = ['mobile'].includes(size)

    const strategyContent = (
      <StrategyHover>
          <span>
              {pipeline.strategy.length > 1
                ? <em>Combined ({pipeline.strategy.length})</em>
                : pipeline.strategy.length > 0 && pipeline.strategy[0].name}
          </span>
          <div className="tooltip">
              {pipeline.strategy.map((strategy, index) => (
                <div key={index} style={{marginBottom: index + 1 !== pipeline.strategy.length ? 10 : 0}}>
                    <div style={{color: 'var(--text)', fontWeight: 600, marginBottom: 3}}>
                        {strategy.name}
                    </div>
                    {Object.keys(strategy.params).map((param) => (
                      <div key={param} style={{fontFamily: 'var(--font-mono)', fontSize: 11}}>
                          {param}: <span style={{color: 'var(--text)'}}>{String(strategy.params[param])}</span>
                      </div>
                    ))}
                </div>
              ))}
          </div>
      </StrategyHover>
    )

    return (
        <BotCard as="div">
            <BotInfo>
                <BotHeader>
                    <BotName $color={getBotColor(pipeline.color)}>
                        <span>{pipeline.name}</span>
                    </BotName>
                    <Tag color={pipeline.paperTrading ? theme.blue : theme.accent}>
                        {pipeline.paperTrading ? "Test" : "Live"}
                    </Tag>
                    <Tag color={pipeline.active ? GREEN : theme.textFaint}>
                        <StatusDot $running={pipeline.active}/>
                        &nbsp;{pipeline.active ? "Running" : "Stopped"}
                    </Tag>
                    {positionSide && (
                      <Tag color={positionColor}>{positionSide}</Tag>
                    )}
                </BotHeader>
                <StatsGrid>
                    <Stat label="Trading Pair" value={pipeline.symbol} color={YELLOW} size="sm"/>
                    <Stat label="Strategy" value={strategyContent} size="sm"/>
                    <Stat label="Candle Size" value={pipeline.candleSize} size="sm"/>
                    <Stat label="Exchange" value={pipeline.exchange} size="sm"/>
                    <Stat label="Active Since" value={age} size="sm"/>
                    <Stat
                      label="PnL (ROI%)"
                      value={`${pipelinePnl.toFixed(2)} USDT`}
                      sub={<span style={{fontFamily: 'var(--font-mono)', fontSize: 11, color: pnlColor}}>
                          {pipelinePnlPct.toFixed(2)}%
                      </span>}
                      color={pnlColor}
                      size="sm"
                    />
                    <Stat label="Allocated Equity" value={`${pipeline.initialEquity} USDT`} size="sm"/>
                    <Stat label="Leverage" value={`×${pipeline.leverage}`} size="sm"/>
                    <Stat label="# Trades" value={pipeline.numberTrades} size="sm"/>
                </StatsGrid>
            </BotInfo>
            <Actions>
                <PipelineButton
                  pipeline={pipeline}
                  startPipeline={startPipeline}
                  stopPipeline={stopPipeline}
                />
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
                      icon={<Pencil/>}
                      fullWidth
                      disabled={pipeline.active}
                      onClick={(event) => {
                          event.preventDefault();
                          event.stopPropagation()
                      }}
                    >
                        Edit Bot
                    </Button>
                </NewPipeline>
                <PipelineDeleteButton
                  pipeline={pipeline}
                  deletePipeline={deletePipeline}
                  stopPipeline={stopPipeline}
                  open={open}
                  setOpen={setOpen}
                />
            </Actions>
        </BotCard>
    );
}


export default PipelineItem;
