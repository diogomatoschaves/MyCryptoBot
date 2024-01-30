import '../App.css';
import {Component} from 'react'
import {Route, Switch, Redirect} from 'react-router-dom'
import {Location} from 'history'
import styled from 'styled-components'
import {
    DropdownOptions,
    MenuOption,
    PipelineParams,
    Position,
    StartPipeline,
    StopPipeline,
    GetCurrentPrices,
    UpdateMessage,
    DeletePipeline,
    BalanceObj,
    Decimals,
    RawTrade,
    PipelinesMetrics,
    RawPipeline,
    PipelinesObject, TradesObject, EditPipeline, EquityTimeSeries, Strategy
} from "../types";
import {
    getTrades,
    getPipelines,
    getPositions,
    getResources,
    getFuturesAccountBalance,
    startBot,
    stopBot,
    getPrice,
    deleteBot, getPipelinesMetrics, editBot, getEquityTimeSeries,
} from "../apiCalls";
import {RESOURCES_MAPPING} from "../utils/constants";
import MenuWrapper from "./MenuWrapper";
import PipelinePanel from "./PipelinePanel";
import TradesPanel from "./TradesPanel";
import {parseTrade, organizePositions, organizePipeline} from "../utils/helpers";
import PositionsPanel from "./PositionsPanel";
import {StyledSegment} from "../styledComponents";
import Dashboard from "./Dashboard";
import {Header, Label} from "semantic-ui-react";
import {balanceReducer} from "../reducers/balancesReducer";


const AppDiv: any = styled.div`
  text-align: center;
  width: 100vw;
  height: 100vh;
  position: absolute;
  justify-content: flex-start;
`

const AppColumn: any = styled.div`
    position: absolute;
    left: ${(props: any) => ['mobile', 'tablet'].includes(props.size) ? 0 : 'min(25vw, 300px)'};
    bottom: 0;
    top: 0;
    right: 0;
    width: ${(props: any) => ['mobile', 'tablet'].includes(props.size) ? '100vw' : 'calc(100vw - min(25vw, 300px))'};
    height: 100vh;
    overflow-x: ${(props: any) => props.overflowX ? props.overflowX : 'hidden'};
`

interface State {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: Strategy[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    trades: TradesObject;
    pipelines: PipelinesObject;
    positions: Position[];
    balances: BalanceObj
    equityTimeSeries: EquityTimeSeries
    menuOption: MenuOption,
    symbols: string[],
    currentPrices: Object
    pipelinesMetrics: PipelinesMetrics
}

interface Props {
    size: string
    location: Location
    history: History
    removeToken: () => void
    decimals: Decimals
    menuProperties: MenuOption[]
    updateMessage: UpdateMessage
}


class App extends Component<Props, State> {

    messageTimeout: any
    getPricesInterval: any
    getTradesInterval: any
    getPositionsInterval: any
    getPipelinesInterval: any

    static defaultProps = {
        decimals: {
            quoteDecimal: 1,
            baseDecimal: 3
        },
        menuProperties: [
            {icon: 'line graph', emoji: '📈', text: 'Dashboard', code: "/dashboard"},
            {icon: 'play', emoji: '🤖', text: 'Trading Bots', code: "/pipelines"},
            {icon: 'list', emoji: '📒', text: 'Positions', code: "/positions"},
            {icon: 'dollar', emoji: '💵', text: 'Trades', code: "/trades"},
        ]
    }

    state = {
        symbolsOptions: [],
        strategiesOptions: [],
        candleSizeOptions: [],
        exchangeOptions: [],
        trades: {},
        pipelines: {},
        positions: [],
        balances: {
            test: {USDT: {availableBalance: 0, totalBalance: 0}},
            live: {USDT: {availableBalance: 0, totalBalance: 0}}
        },
        equityTimeSeries: {
            test: [],
            live: []
        },
        menuOption: {
            icon: 'line graph',
            emoji: '📈',
            text: 'Dashboard',
            code: '/dashboard'
        },
        symbols: [],
        currentPrices: {},
        pipelinesMetrics: {
            totalPipelines: 0,
            activePipelines: 0,
            bestWinRate: {winRate: 0},
            mostTrades: {totalTrades: 0}
        },
    }

    componentDidMount() {
        getResources(Object.keys(RESOURCES_MAPPING), this.props.history)
            .then(resources => {

                const options = resources ? Object.keys(resources).reduce((accum: any, resource: any) => {
                    const resourcesArray = resource === 'candleSizes' ? resources[resource] : Object.keys(resources[resource])
                    return {
                        ...accum,
                        [RESOURCES_MAPPING[resource]]: resourcesArray.map((name: any, index: number) => ({
                            key: index + 1,
                            text: resource !== 'candleSizes' ? resources[resource][name].name : name,
                            value: index + 1,
                            ...(resource !== 'candleSizes' && resources[resource][name])
                        }))
                    }
                }, {}) : []

                this.setState(state => {
                    return {
                        ...state,
                        ...options
                    }
                })
            })
            .catch(() => {})

        this.updateTrades()

        this.updatePipelines()

        this.updatePositions()

        this.getAccountBalance()

        this.getTotalEquityTimeSeries()

        this.updatePipelinesMetrics()
    }

    componentDidUpdate(prevProps: Readonly<Props>, prevState: Readonly<State>, snapshot?: any) {

        const { symbols, trades } = this.state

        if (prevState.symbols.length !== symbols.length) {
            this.getCurrentPrices()
        }

        const { pathname } = this.props.location

        if (prevProps.location.pathname !== pathname) {

            clearInterval(this.getPricesInterval)
            clearInterval(this.getTradesInterval)
            clearInterval(this.getPositionsInterval)
            clearInterval(this.getPipelinesInterval)

            if (pathname.includes('/dashboard')) {
                this.getAccountBalance()
                this.getTotalEquityTimeSeries()
                this.getCurrentPrices()
                this.getPricesInterval = setInterval(() => {
                    this.getCurrentPrices()
                }, 10 * 1000)

            } else if (pathname.includes('/trades')){
                this.updateTrades()
                this.getCurrentPrices()
                this.getTradesInterval = setInterval(() => {
                    this.updateTrades()
                }, 20 * 1000)
            } else if (pathname.includes('/pipelines')){
                this.updatePipelines()
                this.getCurrentPrices()
                this.getPipelinesInterval = setInterval(() => {
                    this.updatePipelines()
                }, 10 * 1000)
            } else if (pathname.includes('/positions')){
                this.updatePositions()
                this.getCurrentPrices()

                this.getPricesInterval = setInterval(() => {
                    this.getCurrentPrices()
                }, 10 * 1000)
                this.getPositionsInterval = setInterval(() => {
                    this.updatePositions()
                }, 30 * 1000)
            }
        }

        if (prevState.trades !== trades) {
            this.updatePipelinesMetrics()
        }
    }

    startPipeline: StartPipeline = (pipelineParams: PipelineParams) => {
        return startBot(pipelineParams)
            .then(response => {

                const { updateMessage } = this.props
                const { strategiesOptions} = this.state

                updateMessage({
                    text: response.message,
                    success: response.success,
                })

                this.setState(state => {
                    const {[pipelineParams.pipelineId as any]: _, ...pipelines} = state.pipelines
                    return {
                        pipelines: response.success ? {
                            ...pipelines,
                            [response.pipeline.id]: organizePipeline(response.pipeline, strategiesOptions)
                        } : state.pipelines
                    }
                })
            })
            .catch(() => {})
    }

    stopPipeline: StopPipeline = (pipelineId) => {
        return stopBot({pipelineId})
            .then(response => {
                const { updateMessage } = this.props
                const { strategiesOptions} = this.state

                updateMessage({
                    text: response.message,
                    success: response.success,
                })

                this.setState(state => {
                    return {
                        pipelines: response.success ? {
                            ...state.pipelines,
                            [pipelineId]: organizePipeline(response.pipeline, strategiesOptions)
                        } : state.pipelines
                    }
                })

                this.updateTrades()
            })
            .catch(() => {})
    }

    editPipeline: EditPipeline = (pipelineParams: PipelineParams, pipelineId?: number) => {
        return editBot(pipelineParams, pipelineId)
          .then(response => {

              const { updateMessage } = this.props
              const { strategiesOptions} = this.state

              updateMessage({
                  text: response.message,
                  success: response.success,
              })

              this.setState(state => {
                  const {[pipelineParams.pipelineId as any]: _, ...pipelines} = state.pipelines
                  return {
                      pipelines: response.success ? {
                          ...pipelines,
                          [response.pipeline.id]: organizePipeline(response.pipeline, strategiesOptions)
                      } : state.pipelines
                  }
              })
          })
          .catch(() => {})
    }

    deletePipeline: DeletePipeline = (pipelineId) => {
        return deleteBot(pipelineId)
            .then(response => {
                const { updateMessage } = this.props

                updateMessage({
                    text: response.message,
                    success: response.success,
                })

                this.setState(state => {
                    const {[pipelineId]: _, ...pipelines} = state.pipelines
                    return {
                        pipelines: response.success ? pipelines : state.pipelines,
                        positions: response.success ? state.positions.reduce(
                        (newPositions: Position[], position: Position) => {
                          return position.pipelineId === pipelineId ? newPositions : [...newPositions, position]
                        },
                        []
                        ) : state.positions
                    }
                })
            })
            .catch(() => {})
    }

    getCurrentPrices: GetCurrentPrices = () => {
        Array.isArray(this.state.symbols) && Promise.allSettled(
            this.state.symbols.map(symbol => getPrice(symbol))
        ).then(results => {
            this.setState({
                currentPrices: results.reduce((prices, result) => {
                    if (result.status === 'fulfilled') {
                        return {...prices, [result.value.symbol]: Number(result.value.price)}
                    } else return prices
                }, {})
            })
        }).catch(() => {})
    }

    getTotalEquityTimeSeries = () => {
        getEquityTimeSeries({pipelineId: null, timeFrame: '15m'})
          .then(response => {
              this.setState({
                equityTimeSeries: {
                    live: response.data.live,
                    test: response.data.testnet,
                }
              })
          })
          .catch(() => {})
    }

    getAccountBalance = () => {
        getFuturesAccountBalance()
          .then(response => {
              this.setState(state => {
                  return {
                      ...state,
                      balances: {
                          live: response.live && response.live.reduce(balanceReducer, {}),
                          test: response.testnet && response.testnet.reduce(balanceReducer, {})
                      }
                  }
              })
          })
          .catch(() => {})
    }

    updatePipelinesMetrics = () => {
        getPipelinesMetrics()
          .then(response => {
              this.setState({
                  pipelinesMetrics: response
              })
          })
          .catch(() => {})
    }

    updateTrades = (page?: number, pipelineId?: string) => {
        getTrades(page, pipelineId)
          .then(response => {
              this.setState(state => {
                  return {
                      ...state,
                      trades: {...state.trades, ...response.trades.reduce((trades: Object, trade: RawTrade) => {
                          return {
                              ...trades,
                              [trade.id]: parseTrade(trade)
                          }
                      }, {})},
                  }
              })
          })
          .catch(() => {})
    }

    updatePipelines = () => {
        getPipelines()
          .then(response => {
              this.setState(state => {
                  return {
                      ...state,
                      pipelines: {...state.pipelines, ...response.pipelines.reduce((pipelines: PipelinesObject, pipeline: RawPipeline) => {
                          return {
                              ...pipelines,
                              [pipeline.id]: organizePipeline(pipeline, state.strategiesOptions)
                          }
                      }, {})},
                  }
              })
          })
          .catch(() => {})
    }

    updatePositions = () => {
        getPositions()
          .then(positions => {
              this.setState(state => {
                  const newPositions = organizePositions(positions.positions)
                  return {
                      ...state,
                      positions: newPositions,
                      // @ts-ignore
                      symbols: [...new Set(newPositions.map(position => position.symbol))]
                  }
              })
          })
          .catch(() => {})
    }

    render() {

        const {
            symbolsOptions,
            strategiesOptions,
            candleSizeOptions,
            exchangeOptions,
            balances,
            trades,
            pipelines,
            positions,
            currentPrices,
            pipelinesMetrics,
            equityTimeSeries,
        } = this.state

        const { size, decimals, menuProperties, location, removeToken, updateMessage } = this.props

        const menuOption = menuProperties.find(option => location.pathname.includes(option.code))

        return (
            <AppDiv className="flex-row">
                <MenuWrapper
                  menuOption={menuOption}
                  menuProperties={menuProperties}
                  removeToken={removeToken}
                  updateMessage={updateMessage}
                  size={size}
                />
                <AppColumn size={size} overflowX={menuOption && menuOption.code === '/positions' && "scroll"} >
                    <StyledSegment
                        basic
                        paddingTop="10px"
                        padding="0"
                        className="flex-column"
                    >
                        {menuOption && (
                          <Header size={'large'} style={{height: '40px', marginTop: '10px'}}>
                              <Label size={'big'}>
                                {menuOption.text}
                                <span style={{marginLeft: 10}}>{menuOption.emoji}</span>
                              </Label>
                          </Header>
                        )}
                        <Switch>
                            <Route path='/trades' exact={true}>
                                <TradesPanel
                                  size={size}
                                  trades={trades}
                                  pipelines={pipelines}
                                  currentPrices={currentPrices}
                                  decimals={decimals}
                                  updateTrades={this.updateTrades}
                                />
                            </Route>
                            <Route path="/pipelines/:pipelineId?" render={({match}) => (
                                <PipelinePanel
                                  size={size}
                                  match={match}
                                  symbolsOptions={symbolsOptions}
                                  strategiesOptions={strategiesOptions}

                                  candleSizeOptions={candleSizeOptions}
                                  exchangeOptions={exchangeOptions}
                                  pipelines={pipelines}
                                  positions={positions}
                                  balances={balances}
                                  startPipeline={this.startPipeline}
                                  stopPipeline={this.stopPipeline}
                                  editPipeline={this.editPipeline}
                                  deletePipeline={this.deletePipeline}
                                  updateMessage={updateMessage}
                                  decimals={decimals}
                                  trades={trades}
                                  currentPrices={currentPrices}
                                  updateTrades={this.updateTrades}
                                />
                              )}/>
                            <Route path="/dashboard">
                                <Dashboard
                                  balances={balances}
                                  size={size}
                                  pipelines={pipelines}
                                  trades={trades}
                                  positions={positions}
                                  currentPrices={currentPrices}
                                  pipelinesMetrics={pipelinesMetrics}
                                  equityTimeSeries={equityTimeSeries}
                                  updatePipelinesMetrics={this.updatePipelinesMetrics}
                                />
                            </Route>
                            <Route path="/positions">
                                <PositionsPanel
                                  size={size}
                                  positions={positions}
                                  pipelines={pipelines}
                                  currentPrices={currentPrices}
                                  decimals={decimals}
                                />
                            </Route>
                            <Route path="*">
                                <Redirect to="/dashboard" />
                            </Route>
                        </Switch>
                        {this.props.children}
                    </StyledSegment>
                </AppColumn>
            </AppDiv>
        );
    }
}


export default App;
