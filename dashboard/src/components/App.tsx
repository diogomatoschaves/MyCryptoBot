import '../App.css';
import {Component} from 'react'
import styled from 'styled-components'
import {
    ChangeMenu,
    DropdownOptions, MenuOption,
    Order, Pipeline, PipelineParams,
    StartPipeline,
    StopPipeline
} from "../types";
import {getOrders, getPipelines, getResources, startBot, stopBot} from "../apiCalls";
import {RESOURCES_MAPPING} from "../utils/constants";
import Menu from "./Menu";
import Wrapper from "../styledComponents/Wrapper";
import PipelinePanel from "./PipelinePanel";
import OrdersPanel from "./OrdersPanel";
import {organizeOrders} from "../utils/helpers";
import PositionsPanel from "./PositionsPanel";


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
    message: string;
    menuOption: MenuOption,
    strategies: any
}


class App extends Component<any, State> {

    state = {
        symbolsOptions: [],
        strategiesOptions: [],
        candleSizeOptions: [],
        exchangeOptions: [],
        orders: [],
        pipelines: [],
        strategies: {},
        message: '',
        menuOption: {
            icon: 'line graph',
            emoji: '📈',
            text: 'Balance',
            code: "balance"
        }
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
                        orders: organizeOrders(orders.orders)
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
                            orders: organizeOrders(orders.orders)
                        }
                    })
                })
        }, 60 * 1000)
    }

    startPipeline: StartPipeline = (pipelineParams: PipelineParams) => {
        startBot(pipelineParams)
            .then(message => {
                this.setState(state => ({
                    message: message.response,
                    pipelines: message.success ? [...state.pipelines, {
                        id: message.pipeline_id,
                        symbol: pipelineParams.symbol,
                        strategy: pipelineParams.strategy,
                        exchange: pipelineParams.exchanges,
                        candleSize: pipelineParams.candleSize,
                        params: pipelineParams.params,
                        paperTrading: pipelineParams.paperTrading,
                        active: true
                    }] : state.pipelines
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
            menuOption,
            strategies
        } = this.state

        return (
            <AppDiv className="flex-row">
                <Menu menuOption={menuOption} changeMenu={this.changeMenu}/>
                <Wrapper>
                    {menuOption.code === 'pipelines' ? (
                        <PipelinePanel
                            menuOption={menuOption}
                            symbolsOptions={symbolsOptions}
                            strategiesOptions={strategiesOptions}
                            candleSizeOptions={candleSizeOptions}
                            exchangeOptions={exchangeOptions}
                            pipelines={pipelines}
                            strategies={strategies}
                            startPipeline={this.startPipeline}
                            stopPipeline={this.stopPipeline}
                        />
                    ) : menuOption.code === 'transactions' ? (
                        <OrdersPanel menuOption={menuOption} orders={orders}/>
                    ) : menuOption.code === 'positions' && (
                        <PositionsPanel menuOption={menuOption}/>
                    )}

                </Wrapper>

            </AppDiv>
        );
    }
}

export default App;
