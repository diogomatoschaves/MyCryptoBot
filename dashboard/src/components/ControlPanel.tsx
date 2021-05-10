import {Divider, Grid} from "semantic-ui-react";
import PipelinePanel from "./PipelinePanel";
import OrdersPanel from "./OrdersPanel";
import {ActivePipeline, DropdownOptions, Order, StartPipeline, StopPipeline} from "../types";
import styled from "styled-components";


interface Props {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    orders: Order[];
    activePipelines: ActivePipeline[]
    startPipeline: StartPipeline
    stopPipeline: StopPipeline
}


const Wrapper = styled.div`
    height: calc(100% - 50px);
    width: 100%;
`

const Column = styled.div`
    height: 100%;
    width: 50%;
`


function ControlPanel(props: Props) {

    const {
        symbolsOptions,
        strategiesOptions,
        candleSizeOptions,
        exchangeOptions,
        orders,
        activePipelines,
        startPipeline,
        stopPipeline
    } = props

    return (
        <Wrapper className="flex-row">
            <Column style={{overflowY: 'scroll'}}>
                <PipelinePanel
                    symbolsOptions={symbolsOptions}
                    strategiesOptions={strategiesOptions}
                    candleSizeOptions={candleSizeOptions}
                    exchangeOptions={exchangeOptions}
                    activePipelines={activePipelines}
                    startPipeline={startPipeline}
                    stopPipeline={stopPipeline}
                />
            </Column>
            <Column style={{overflowY: 'scroll'}}>
                <OrdersPanel orders={orders}/>
            </Column>
        </Wrapper>
    );
}

export default ControlPanel;
