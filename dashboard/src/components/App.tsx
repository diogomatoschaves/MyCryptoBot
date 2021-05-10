import '../App.css';
import {Component} from 'react'
import styled from 'styled-components'
import {Header} from "semantic-ui-react";
import ControlPanel from "./ControlPanel";
import {ActivePipeline, DropdownOptions, Order, PipelineParams, StartPipeline, StopPipeline} from "../types";
import {getOrders, getResources, startBot, stopBot} from "../apiCalls";
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
    activePipelines: ActivePipeline[];
    message: string
}


class App extends Component<any, State> {

    state = {
        symbolsOptions: [],
        strategiesOptions: [],
        candleSizeOptions: [],
        exchangeOptions: [],
        orders: [],
        activePipelines: [],
        message: ''
    }

    componentDidMount() {
        getResources(Object.keys(RESOURCES_MAPPING))
            .then(resources => {
                const options = Object.keys(resources).reduce((accum: any, resource: any) => {
                    return {
                        ...accum,
                        [RESOURCES_MAPPING[resource]]: resources[resource].map((item: any, index: number) => ({
                            key: index + 1,
                            text: item.name,
                            value: index + 1
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

    startPipeline: StartPipeline = (pipelineParams: PipelineParams) => {
        startBot(pipelineParams)
            .then(message => {
                this.setState(state => ({
                    message: message.response,
                    activePipelines: message.success ? [...state.activePipelines, {
                        symbol: pipelineParams.symbol,
                        strategy: pipelineParams.strategy,
                        exchange: pipelineParams.exchanges,
                        candleSize: pipelineParams.candleSize
                    }] : state.activePipelines
                }))
            })
    }

    stopPipeline: StopPipeline = ({symbol, exchange}) => {
        stopBot({symbol, exchange})
            .then(message => {
                this.setState(state => ({
                    message: message.response,
                    activePipelines: message.success ? state.activePipelines.reduce(
                        (newArray: ActivePipeline[], pipeline: ActivePipeline) => {
                            if (symbol === pipeline.symbol && exchange === pipeline.exchange) {
                                return newArray
                            } else return [...newArray, pipeline]
                        },
                        []
                    ) : state.activePipelines
                }))
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
                    startPipeline={this.startPipeline}
                    stopPipeline={this.stopPipeline}
                />
            </AppDiv>
        );
    }
}

export default App;
