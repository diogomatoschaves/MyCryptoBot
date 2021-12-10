import {Button, Dropdown, Grid, Divider, TextArea, Form, Modal, Header, Icon} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {ActivePipeline, DropdownOptions, StartPipeline, StopPipeline, Pipeline} from "../types";
import {useState} from "react";
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
    stopPipeline: StopPipeline
}



const ButtonWrapper = styled.div`
    height: 50px; 
    margin-bottom: 30px;
    width: 100%;
    justify-content: flex-end;
`

function PipelinePanel(props: Props) {

    const {
        symbolsOptions,
        strategiesOptions,
        pipelines,
        candleSizeOptions,
        exchangeOptions,
        startPipeline,
        stopPipeline
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
            <Divider horizontal style={{marginBottom: '20px', marginTop: '0'}}>Pipelines</Divider>
            <ButtonWrapper className="flex-row">
                <NewPipeline
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


const styles = {

}


// <Divider horizontal style={{marginBottom: '30px', marginTop: 0}}>Bot Control Panel</Divider>
