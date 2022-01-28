import {Button, Divider, Icon} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {DropdownOptions, StartPipeline, StopPipeline, Pipeline, MenuOption, Trade} from "../types";
import PipelineItem from './Pipeline'
import NewPipeline from "./NewPipeline";
import styled from "styled-components";
import {useEffect, useReducer, useRef, useState} from "react";


interface Props {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    pipelines: Pipeline[];
    startPipeline: StartPipeline;
    stopPipeline: StopPipeline;
    menuOption: MenuOption;
    strategies: any
}


const ButtonWrapper = styled.div`
    margin-bottom: 40px;
    width: 100%;
    justify-content: space-around;
`

const FILTER_PIPELINES = 'FILTER_PIPELINES'


const reducer = (state: any, action: any) => {
    switch (action.type) {
        case FILTER_PIPELINES:
            const { pipelines } = action
            return {
                ...state,
                liveActivePipelines: pipelines.filter(
                    (pipeline: Pipeline) => pipeline.active && !pipeline.paperTrading
                ),
                demoActivePipelines: pipelines.filter(
                    (pipeline: Pipeline) => pipeline.active && pipeline.paperTrading
                ),
                liveStoppedPipelines: pipelines.filter(
                    (pipeline: Pipeline) => !pipeline.active && !pipeline.paperTrading)
                ,
                demoStoppedPipelines: pipelines.filter(
                    (pipeline: Pipeline) => !pipeline.active && pipeline.paperTrading
                ),
            }
        default:
            throw new Error();
    }
}

function PipelinePanel(props: Props) {

    const {
        symbolsOptions,
        strategiesOptions,
        pipelines,
        strategies,
        candleSizeOptions,
        exchangeOptions,
        startPipeline,
        stopPipeline,
        menuOption
    } = props

    const previous = useRef({ pipelines }).current;

    const [live, filterLive] = useState(true)
    const [active, filterActive] = useState(true)

    const [
        {
            liveActivePipelines,
            demoActivePipelines,
            liveStoppedPipelines,
            demoStoppedPipelines,
        }, dispatch
    ] = useReducer(
        reducer, {
            liveActivePipelines: pipelines.filter(
                (pipeline: Pipeline) => pipeline.active && !pipeline.paperTrading
            ),
            demoActivePipelines: pipelines.filter(
                (pipeline: Pipeline) => pipeline.active && pipeline.paperTrading
            ),
            liveStoppedPipelines: pipelines.filter(
                (pipeline: Pipeline) => !pipeline.active && !pipeline.paperTrading)
            ,
            demoStoppedPipelines: pipelines.filter(
                (pipeline: Pipeline) => !pipeline.active && pipeline.paperTrading
            ),
        }
    );

    useEffect(() => {
        if (pipelines !== previous.pipelines) {
            console.log("pipelines updated")
            dispatch({
                type: FILTER_PIPELINES,
                pipelines
            })
        }
        return () => {
            previous.pipelines = pipelines
        };
    }, [pipelines]);

    const filteredPipelines = (live && active) ? liveActivePipelines : (live && !active) ? liveStoppedPipelines :
        (!live && active) ? demoActivePipelines : demoStoppedPipelines

    return (
        <StyledSegment basic className="flex-column">
            <Divider horizontal style={{marginBottom: '20px', marginTop: '0'}}>
                <span>{menuOption.emoji}</span> {menuOption.text}
            </Divider>
            <ButtonWrapper className="flex-row">
                <Button.Group size="mini" style={{alignSelf: 'center'}}>
                    <Button onClick={() => filterActive(true)} secondary={active}>
                        Running
                    </Button>
                    <Button onClick={() => filterActive(false)} secondary={!active}>
                        Stopped
                    </Button>
                </Button.Group>
                <Button.Group size="mini" style={{alignSelf: 'center'}}>
                    <Button onClick={() => filterLive(true)} secondary={live}>
                        Live
                    </Button>
                    <Button onClick={() => filterLive(false)} secondary={!live}>
                        Demo
                    </Button>
                </Button.Group>
                <NewPipeline
                    strategies={strategies}
                    symbolsOptions={symbolsOptions}
                    strategiesOptions={strategiesOptions}
                    candleSizeOptions={candleSizeOptions}
                    exchangeOptions={exchangeOptions}
                    startPipeline={startPipeline}
                />
            </ButtonWrapper>
            {filteredPipelines.map((pipeline: Pipeline) => (
                <PipelineItem
                    startPipeline={startPipeline}
                    stopPipeline={stopPipeline}
                    pipeline={pipeline}
                    live={live}
                />
            ))}
            {filteredPipelines.length === 0 && (
                <span>"There are no trading bots that match the chosen filters."</span>
            )}
        </StyledSegment>
    );
}

export default PipelinePanel;
