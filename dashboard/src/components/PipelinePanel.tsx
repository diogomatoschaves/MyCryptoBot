import {Divider, Icon} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {DropdownOptions, StartPipeline, StopPipeline, Pipeline, MenuOption} from "../types";
import PipelineItem from './Pipeline'
import NewPipeline from "./NewPipeline";
import styled from "styled-components";


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
    height: 50px; 
    margin-bottom: 30px;
    width: 100%;
    justify-content: center;
`

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

    const filteredPipelines = pipelines.sort((a, b) => {

        if (a.active && b.active) {
            return 0
        } else if (a.active && !b.active) {
            return -1
        } else if (!a.active && b.active) {
            return 1
        } else {
            return 0
        }
    })

    return (
        <StyledSegment basic className="flex-column">
            <Divider horizontal style={{marginBottom: '20px', marginTop: '0'}}>
                <span>{menuOption.emoji}</span> Trading Bots
            </Divider>
            <ButtonWrapper className="flex-row">
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
                />
            ))}
        </StyledSegment>
    );
}

export default PipelinePanel;
