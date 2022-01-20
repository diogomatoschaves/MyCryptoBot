import '../App.css';
import {Component} from 'react'
import styled from 'styled-components'
import {
    ChangeMenu,
    DropdownOptions, MenuOption,
    Trade, Pipeline, PipelineParams, Position,
    StartPipeline,
    StopPipeline, GetCurrentPrices
} from "../types";
import {getTrades, getPipelines, getPositions, getResources, startBot, stopBot, getPrice} from "../apiCalls";
import {RESOURCES_MAPPING} from "../utils/constants";
import Menu from "./Menu";
import Wrapper from "../styledComponents/Wrapper";
import PipelinePanel from "./PipelinePanel";
import TradesPanel from "./TradesPanel";
import {organizeTrades, organizePositions} from "../utils/helpers";
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
    trades: Trade[];
    pipelines: Pipeline[];
    positions: Position[];
    message: string;
    menuOption: MenuOption,
    strategies: any
    symbols: string[],
    currentPrices: Object
}


class App extends Component<any, State> {

    state = {
        symbolsOptions: [],
        strategiesOptions: [],
        candleSizeOptions: [],
        exchangeOptions: [],
        trades: [],
        pipelines: [],
        positions: [],
        strategies: {},
        message: '',
        menuOption: {
            icon: 'line graph',
            emoji: '📈',
            text: 'Balance',
            code: "balance"
        },
        symbols: [],
        currentPrices: {}
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

        getTrades()
            .then(response => {
                this.setState(state => {
                    return {
                        ...state,
                        trades: organizeTrades(response.trades)
                    }
                })
            })

        getPipelines()
            .then(pipelines => {
                this.setState(state => {
                    return {
                        ...state,
                        ...pipelines,
                        // @ts-ignore
                        symbols: [...new Set(pipelines.pipelines.map(pipeline => pipeline.symbol))]
                    }
                })

                this.getCurrentPrices()
            })

        getPositions()
            .then(positions => {
                this.setState(state => {
                    return {
                        ...state,
                        positions: organizePositions(positions.positions)
                    }
                })
            })

        setInterval(() => {
            getTrades()
                .then(response => {
                    this.setState(state => {
                        return {
                            ...state,
                            trades: organizeTrades(response.trades)
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
                        id: message.pipelineId,
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
                                return [
                                    ...newArray, {
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

    getCurrentPrices: GetCurrentPrices = () => {
        Promise.allSettled(
            this.state.symbols.map(symbol => getPrice(symbol))
        ).then(results => {
            this.setState({
                currentPrices: results.reduce((prices, result) => {
                    if (result.status === 'fulfilled') {
                        return {...prices, [result.value.symbol]: Number(result.value.price)}
                    } else return prices
                }, {})
            })
        })
    }

    render(){

        const {
            symbolsOptions,
            strategiesOptions,
            candleSizeOptions,
            exchangeOptions,
            trades,
            pipelines,
            positions,
            menuOption,
            strategies,
            currentPrices
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
                    ) : menuOption.code === 'trades' ? (
                        <TradesPanel menuOption={menuOption} trades={trades} currentPrices={currentPrices}/>
                    ) : menuOption.code === 'positions' && (
                        <PositionsPanel menuOption={menuOption} positions={positions}/>
                    )}

                </Wrapper>

            </AppDiv>
        );
    }
}

export default App;
