import {Fragment, useEffect, useReducer, useRef} from 'react'
import {Link} from 'react-router-dom';
import styled from "styled-components";
import {Bot, Plus} from 'lucide-react'
import {
    DropdownOptions,
    StartPipeline,
    StopPipeline,
    UpdateMessage,
    DeletePipeline,
    BalanceObj,
    PipelinesObject,
    Decimals,
    TradesObject,
    UpdateTrades,
    Position,
    EditPipeline, Strategy
} from "../types";
import PipelineItem from './Pipeline'
import NewPipeline from "./NewPipeline";
import PipelineDetail from "./PipelineDetail";
import {Button, EmptyState, SegmentedControl} from "../ui";


const Toolbar = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    flex-wrap: wrap;
    margin-bottom: 22px;
    animation: fadeUp 0.3s ease both;
`

const Filters = styled.div`
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
`

const BotList = styled.div`
    display: flex;
    flex-direction: column;
    width: 100%;

    & > a {
        animation: fadeUp 0.35s ease both;
    }
    & > a:nth-child(2) { animation-delay: 0.05s; }
    & > a:nth-child(3) { animation-delay: 0.1s; }
    & > a:nth-child(4) { animation-delay: 0.15s; }
    & > a:nth-child(5) { animation-delay: 0.2s; }
`


interface Props {
    size: string
    symbolsOptions: DropdownOptions[];
    strategiesOptions: Strategy[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    pipelines: PipelinesObject;
    positions: Position[];
    balances: BalanceObj;
    startPipeline: StartPipeline;
    stopPipeline: StopPipeline;
    editPipeline: EditPipeline;
    deletePipeline: DeletePipeline;
    updateMessage: UpdateMessage;
    match: any
    decimals: Decimals
    trades: TradesObject
    currentPrices: Object
    updateTrades: UpdateTrades
}


const FILTER_PIPELINES = 'FILTER_PIPELINES'
const TOGGLE_OPTIONS = 'TOGGLE_OPTIONS'


const reducer = (state: any, action: any) => {
    switch (action.type) {
        case FILTER_PIPELINES:
            const { pipelines, options: {active, stopped, live, test} } = action

            return {
                ...state,
                filteredPipelines: Object.keys(pipelines).filter((pipelineId: string) => {

                    const pipeline = pipelines[pipelineId]

                    return ((pipeline.active === active && active) || (pipeline.active === !stopped && stopped))
                    && ((pipeline.paperTrading === test && test) || (pipeline.paperTrading === !live && live))
                })
            }
        case TOGGLE_OPTIONS:
            return {
                ...state,
                options: {
                    live: action.live !== undefined ? action.live : state.options.live,
                    test: action.test !== undefined ? action.test : state.options.test,
                    active: action.active !== undefined ? action.active : state.options.active,
                    stopped: action.stopped !== undefined ? action.stopped : state.options.stopped,
                }
            }
        default:
            throw new Error();
    }
}


const initialOptions = {
    live: true,
    test: true,
    active: true,
    stopped: true
}

function PipelinePanel(props: Props) {

    const {
        size,
        symbolsOptions,
        strategiesOptions,
        pipelines,
        positions,
        balances,
        candleSizeOptions,
        exchangeOptions,
        startPipeline,
        stopPipeline,
        editPipeline,
        deletePipeline,
        trades,
        decimals,
        currentPrices,
        updateTrades,
        match: {params: {pipelineId}}
    } = props

    const [
        {
            filteredPipelines,
            options
        }, dispatch
    ] = useReducer(
        reducer, {
            filteredPipelines: Object.keys(pipelines),
            options: initialOptions
        }
    );

    const previous = useRef({ pipelines, options }).current;

    useEffect(() => {
        if (pipelines !== previous.pipelines || options !== previous.options) {
            dispatch({
                type: FILTER_PIPELINES,
                pipelines,
                options
            })
        }
        return () => {
            previous.pipelines = pipelines
            previous.options = options
        };
    }, [pipelines, options, previous]);

    const pipelineMatch = Object.keys(pipelines).find(pipeline => pipeline === pipelineId)

    const isMobile = ['mobile'].includes(size)

    return (
        <Fragment>
            {pipelineMatch ? (
              <PipelineDetail
                size={size}
                pipelines={pipelines}
                pipelineId={pipelineMatch}
                startPipeline={startPipeline}
                stopPipeline={stopPipeline}
                editPipeline={editPipeline}
                deletePipeline={deletePipeline}
                decimals={decimals}
                trades={trades}
                currentPrices={currentPrices}
                updateTrades={updateTrades}
                positions={positions}
                balances={balances}
                symbolsOptions={symbolsOptions}
                strategiesOptions={strategiesOptions}
                candleSizeOptions={candleSizeOptions}
                exchangeOptions={exchangeOptions}
              />
            ) : (
              <div style={{width: '100%'}}>
                <Toolbar>
                    <Filters>
                        <SegmentedControl
                          options={[
                              {value: 'live', label: 'Live'},
                              {value: 'test', label: 'Test'},
                          ]}
                          isActive={(value) => options[value]}
                          onToggle={(value) => dispatch({
                              type: TOGGLE_OPTIONS,
                              [value]: !options[value]
                          })}
                        />
                        <SegmentedControl
                          options={[
                              {value: 'active', label: 'Active'},
                              {value: 'stopped', label: 'Stopped'},
                          ]}
                          isActive={(value) => options[value]}
                          onToggle={(value) => dispatch({
                              type: TOGGLE_OPTIONS,
                              [value]: !options[value]
                          })}
                        />
                    </Filters>
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
                        isMobile={isMobile}
                    >
                        <Button variant="primary" icon={<Plus/>}>
                            New Trading Bot
                        </Button>
                    </NewPipeline>
                </Toolbar>
                <BotList>
                    {filteredPipelines.map((pipelineId: string) => (
                      <Link key={pipelineId} to={`/pipelines/${pipelineId}`}>
                        <PipelineItem
                            size={size}
                            balances={balances}
                            pipelines={pipelines}
                            positions={positions}
                            symbolsOptions={symbolsOptions}
                            strategiesOptions={strategiesOptions}
                            candleSizeOptions={candleSizeOptions}
                            exchangeOptions={exchangeOptions}
                            startPipeline={startPipeline}
                            editPipeline={editPipeline}
                            stopPipeline={stopPipeline}
                            deletePipeline={deletePipeline}
                            pipeline={pipelines[pipelineId]}
                            lastRow={true}
                            position={positions.find((position) => String(position.pipelineId) === pipelineId)}
                        />
                      </Link>
                    ))}
                </BotList>
                {filteredPipelines.length === 0 && (
                    <EmptyState
                      icon={<Bot/>}
                      title="No trading bots match the chosen filters"
                      hint="Adjust the filters above or create a new trading bot."
                    />
                )}
              </div>
            )}
        </Fragment>
    );
}

export default PipelinePanel;
