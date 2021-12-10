import {Divider, Grid, Header} from "semantic-ui-react";
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
    padding-top: 20px;
    height: 100%;
    width: 100%;
    overflow-y: scroll;
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
        <Wrapper className="flex-column">
            <OrdersPanel orders={orders}/>
        </Wrapper>
    );
}

export default ControlPanel;


// <Header size='huge' style={{height: '50px'}}>Crypto Bot Dashboard</Header>
// <Column style={{overflowY: 'scroll'}}>

// </Column>