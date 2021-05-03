import {Divider, Grid} from "semantic-ui-react";
import PipelinePanel from "./PipelinePanel";
import OrdersPanel from "./OrdersPanel";
import {ActivePipeline, DropdownOptions, Order} from "../types";
import styled from "styled-components";


interface Props {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    orders: Order[];
    activePipelines: ActivePipeline[]
}


const Wrapper = styled.div`
    height: 100%;
    width: 100%;
`

const Column = styled.div`
    height: 100%;
    width: 50%;
`


function ControlPanel(props: Props) {

    const { symbolsOptions, strategiesOptions, orders, activePipelines } = props

    return (
        <Wrapper className="flex-row">
            <Column style={{overflowY: 'scroll'}}>
                <PipelinePanel
                    symbolsOptions={symbolsOptions}
                    strategiesOptions={strategiesOptions}
                    activePipelines={activePipelines}
                />
            </Column>
            <Column style={{overflowY: 'scroll'}}>
                <OrdersPanel orders={orders}/>
            </Column>
        </Wrapper>
    );
}

export default ControlPanel;


const styles = {
    gridStyle: {
        width: '100%',
        height: '100%',
        marginTop: '5px'
    },
    leftColumn: {
        borderRight: '1px solid #d2d2d2',
    },
    rightColumn: {
        overflowY: 'scroll'
    }
}
