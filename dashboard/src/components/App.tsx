import '../App.css';
import {Component} from 'react'
import styled from 'styled-components'
import {Header} from "semantic-ui-react";
import ControlPanel from "./ControlPanel";
import {
    ActivePipeline,
    ChangeMenu,
    DropdownOptions,
    Order, Pipeline,
    PipelineParams,
    StartPipeline,
    StopPipeline
} from "../types";
import {getOrders, getPipelines, getResources, startBot, stopBot} from "../apiCalls";
import {RESOURCES_MAPPING} from "../utils/constants";
import Menu from "./Menu";
import Wrapper from "../styledComponents/Wrapper";
import PipelinePanel from "./PipelinePanel";
import OrdersPanel from "./OrdersPanel";


const AppDiv = styled.div`
  text-align: center;
  width: 100vw;
  height: 100vh;
  position: absolute;
  justify-content: flex-start;
`

interface State {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    orders: Order[];
    pipelines: Pipeline[];
    activePipelines: ActivePipeline[];
    message: string;
    menuOption: string
}


class App extends Component<any, State> {

    state = {
        symbolsOptions: [],
        strategiesOptions: [],
        candleSizeOptions: [],
        exchangeOptions: [],
        orders: [],
        pipelines: [],
        activePipelines: [],
        message: '',
        menuOption: 'pipelines'
    }

    componentDidMount() {
        getResources(Object.keys(RESOURCES_MAPPING))
            .then(resources => {
                const options = Object.keys(resources).reduce((accum: any, resource: any) => {
                    return {
                        ...accum,
                        [RESOURCES_MAPPING[resource]]: Object.keys(resources[resource]).map((name: any, index: number) => ({
                            key: index + 1,
                            text: name,
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

        getPipelines()
            .then(pipelines => {
                this.setState(state => {
                    return {
                        ...state,
                        ...pipelines
                    }
                })
            })

        setInterval(() => {
            getOrders()
                .then(orders => {
                    this.setState(state => {
                        return {
                            ...state,
                            ...orders
                        }
                    })
                })
        }, 60 * 1000)
    }

    startPipeline: StartPipeline = (pipelineParams: Pipeline) => {
        startBot(pipelineParams)
            .then(message => {
                this.setState(state => ({
                    message: message.response,
                    activePipelines: message.success ? [...state.activePipelines, {
                        symbol: pipelineParams.symbol,
                        strategy: pipelineParams.strategy,
                        exchange: pipelineParams.exchange,
                        candleSize: pipelineParams.candleSize
                    }] : state.activePipelines
                }))
            })
    }

    stopPipeline: StopPipeline = (pipelineId) => {
        stopBot({pipelineId})
            .then(message => {
                this.setState(state => ({
                    message: message.response,
                    pipelines: message.success ? state.pipelines.reduce(
                        (newArray: Pipeline[], pipeline: Pipeline) => {
                            if (pipelineId === pipeline.id) {
                                return [...newArray, {
                                    ...pipeline,
                                    active: false
                                }]
                            } else return [...newArray, pipeline]
                        },
                        []
                    ) : state.pipelines
                }))
            })
    }

    changeMenu: ChangeMenu = (menuOption) => {
        this.setState({ menuOption })
    }

    render(){

        const {
            symbolsOptions,
            strategiesOptions,
            candleSizeOptions,
            exchangeOptions,
            orders,
            pipelines,
            menuOption
        } = this.state

        return (
            <AppDiv className="flex-row">
                <Menu changeMenu={this.changeMenu}/>
                <Wrapper>
                    {menuOption === 'pipelines' ? (
                        <PipelinePanel
                            symbolsOptions={symbolsOptions}
                            strategiesOptions={strategiesOptions}
                            candleSizeOptions={candleSizeOptions}
                            exchangeOptions={exchangeOptions}
                            pipelines={pipelines}
                            startPipeline={this.startPipeline}
                            stopPipeline={this.stopPipeline}
                        />
                    ) : (
                        <OrdersPanel orders={orders}/>
                    )}

                </Wrapper>

            </AppDiv>
        );
    }
}

export default App;
