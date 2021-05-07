import '../App.css';
import {Component} from 'react'
import styled from 'styled-components'
import {Header} from "semantic-ui-react";
import ControlPanel from "./ControlPanel";
import {ActivePipeline, DropdownOptions, Order} from "../types";
import {getOrders, getResources} from "../apiCalls";
import {RESOURCES_MAPPING} from "../utils/constants";


const AppDiv = styled.div`
  text-align: center;
  width: 100vw;
  height: 100vh;
  position: absolute;
  justify-content: flex-start;
  padding: 20px;
`

interface State {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    orders: Order[];
    activePipelines: ActivePipeline[]
}


class App extends Component<any, State> {

    state = {
        symbolsOptions: [],
        strategiesOptions: [],
        candleSizeOptions: [],
        exchangeOptions: [],
        orders: [],
        activePipelines: []
    }

    componentDidMount() {
        getResources(Object.keys(RESOURCES_MAPPING))
            .then(resources => {
                const options = Object.keys(resources).reduce((accum: any, resource: any) => {
                    return {
                        ...accum,
                        [RESOURCES_MAPPING[resource]]: resources[resource].map((item: any, index: number) => ({
                            key: index,
                            text: item.name,
                            value: index
                        }))
                    }
                }, {})

                this.setState(state => {
                    return {
                        ...state,
                        ...resources,
                        ...options
                    }
                })
            })
            .catch()

        getOrders()
            .then(orders => {
                this.setState(state => {
                    return {
                        ...state,
                        ...orders
                    }
                })
            })
    }

    render(){

        const {
            symbolsOptions,
            strategiesOptions,
            candleSizeOptions,
            exchangeOptions,
            orders,
            activePipelines
        } = this.state

        return (
            <AppDiv className="flex-column">
                <Header size='huge' style={{height: '50px'}}>Crypto Bot Dashboard</Header>
                <ControlPanel
                    symbolsOptions={symbolsOptions}
                    strategiesOptions={strategiesOptions}
                    candleSizeOptions={candleSizeOptions}
                    exchangeOptions={exchangeOptions}
                    orders={orders}
                    activePipelines={activePipelines}
                />
            </AppDiv>
        );
    }
}

export default App;
