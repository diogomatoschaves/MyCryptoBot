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
    PipelinesObject, TradesObject, EditPipeline
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
    deleteBot, getPipelinesMetrics, editBot,
} from "../apiCalls";
import {RESOURCES_MAPPING} from "../utils/constants";
import Menu from "./Menu";
import PipelinePanel from "./PipelinePanel";
import TradesPanel from "./TradesPanel";
import {parseTrade, organizePositions, organizePipeline} from "../utils/helpers";
import PositionsPanel from "./PositionsPanel";
import {StyledSegment} from "../styledComponents";
import Dashboard from "./Dashboard";
import {Header} from "semantic-ui-react";


const AppDiv: any = styled.div`
  text-align: center;
  width: 100vw;
  height: 100vh;
  position: absolute;
  justify-content: flex-start;
`

const MenuColumn = styled.div`
    position: fixed;
    left: 0;
    bottom: 0;
    top: 0;
    width: 25vw;
`

const AppColumn: any = styled.div`
    position: absolute;
    left: 25vw;
    bottom: 0;
    top: 0;
    right: 0;
    width: 75vw;
    height: 100vh;
    overflow-x: ${(props: any) => props.overflowX ? props.overflowX : 'hidden'};
`

interface State {
    symbolsOptions: DropdownOptions[];
    strategiesOptions: DropdownOptions[];
    candleSizeOptions: DropdownOptions[];
    exchangeOptions: DropdownOptions[];
    trades: TradesObject;
    pipelines: PipelinesObject;
    positions: Position[];
    balances: BalanceObj
    menuOption: MenuOption,
    strategies: any
    symbols: string[],
    currentPrices: Object
    pipelinesMetrics: PipelinesMetrics
}

interface Props {
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
        strategies: {},
        balances: {
            test: {USDT: {availableBalance: 0, totalBalance: 0}},
            live: {USDT: {availableBalance: 0, totalBalance: 0}}
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
        }
    }

    componentDidMount() {
        getResources(Object.keys(RESOURCES_MAPPING), this.props.history)
            .then(resources => {
                const options = resources ? Object.keys(resources).reduce((accum: any, resource: any) => {
                    return {
                        ...accum,
                        [RESOURCES_MAPPING[resource]]: Object.keys(resources[resource]).map((name: any, index: number) => ({
                            key: index + 1,
                            text: name,
                            value: index + 1
                        }))
                    }
                }, {}) : []

                this.setState(state => {
                    return {
                        ...state,
                        ...resources,
                        ...options
                    }
                })
            })
            .catch(() => {})

        this.updateTrades()

        this.updatePipelines()

        this.updatePositions()

        this.getAccountBalance()

        this.updatePipelinesMetrics()
    }

    componentDidUpdate(prevProps: Readonly<Props>, prevState: Readonly<State>, snapshot?: any) {

        const { symbols } = this.state

        if (prevState.symbols.length !== symbols.length) {
            this.getCurrentPrices()
        }

        const { pathname } = this.props.location

        if (prevProps.location.pathname !== pathname) {

            clearInterval(this.getPricesInterval)
            clearInterval(this.getTradesInterval)
            clearInterval(this.getPositionsInterval)

            if (pathname.includes('/dashboard')) {
                this.getAccountBalance()
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
    }

    startPipeline: StartPipeline = (pipelineParams: PipelineParams) => {
        return startBot(pipelineParams)
            .then(response => {

                const { updateMessage } = this.props

                updateMessage({
                    text: response.message,
                    success: response.success,
                })

                this.setState(state => {
                    const {[pipelineParams.pipelineId as any]: _, ...pipelines} = state.pipelines
                    return {
                        pipelines: response.success ? {
                            ...pipelines,
                            [response.pipeline.id]: organizePipeline(response.pipeline)
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

                updateMessage({
                    text: response.message,
                    success: response.success,
                })

                this.setState(state => {
                    return {
                        pipelines: response.success ? {
                            ...state.pipelines,
                            [pipelineId]: organizePipeline(response.pipeline)
                        } : state.pipelines
                    }
                })
            })
            .catch(() => {})
    }

    editPipeline: EditPipeline = (pipelineParams: PipelineParams, pipelineId?: number) => {
        return editBot(pipelineParams, pipelineId)
          .then(response => {

              const { updateMessage } = this.props

              updateMessage({
                  text: response.message,
                  success: response.success,
              })

              this.setState(state => {
                  const {[pipelineParams.pipelineId as any]: _, ...pipelines} = state.pipelines
                  return {
                      pipelines: response.success ? {
                          ...pipelines,
                          [response.pipeline.id]: organizePipeline(response.pipeline)
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

    balanceReducer = (balance: any, coin: { asset: string; balance: string; withdrawAvailable: string; }) => {
        return {
            ...balance,
            [coin.asset]: {
                totalBalance: Number(coin.balance),
                availableBalance: Number(coin.withdrawAvailable)
            }
        }
    }

    getAccountBalance = () => {
        getFuturesAccountBalance()
          .then(response => {
              this.setState(state => {
                  return {
                      ...state,
                      balances: {
                          live: response.live.reduce(this.balanceReducer, {}),
                          test: response.testnet.reduce(this.balanceReducer, {})
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
                              [pipeline.id]: organizePipeline(pipeline)
                          }
                      }, {})},
                      // @ts-ignore
                      symbols: [...new Set(response.pipelines.map(pipeline => pipeline.symbol))]
                  }
              })
          })
          .catch(() => {})
    }

    updatePositions = () => {
        getPositions()
          .then(positions => {
              this.setState(state => {
                  return {
                      ...state,
                      positions: organizePositions(positions.positions)
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
            strategies,
            currentPrices,
            pipelinesMetrics,
        } = this.state

        const { decimals, menuProperties, location, removeToken, updateMessage } = this.props

        const menuOption = menuProperties.find(option => location.pathname.includes(option.code))

        return (
            <AppDiv className="flex-row">
                <MenuColumn>
                    <Menu
                      menuOption={menuOption}
                      menuProperties={menuProperties}
                      removeToken={removeToken}
                      updateMessage={updateMessage}
                    />
                </MenuColumn>
                <AppColumn overflowX={menuOption && menuOption.code === '/positions' && "scroll"} >
                    <StyledSegment
                        basic
                        paddingTop="10px"
                        padding="0"
                        className="flex-column"
                    >
                        {menuOption && (
                          <Header size={'large'} dividing style={{height: '40px'}}>
                            <span style={{marginRight: 10}}>{menuOption.emoji}</span>
                            {menuOption.text}
                          </Header>
                        )}
                        <Switch>
                            <Route path='/trades' exact={true}>
                                <TradesPanel
                                  trades={trades}
                                  pipelines={pipelines}
                                  currentPrices={currentPrices}
                                  decimals={decimals}
                                  updateTrades={this.updateTrades}
                                />
                            </Route>
                            <Route path="/pipelines/:pipelineId?" render={({match}) => (
                                <PipelinePanel
                                  match={match}
                                  symbolsOptions={symbolsOptions}
                                  strategiesOptions={strategiesOptions}
                                  candleSizeOptions={candleSizeOptions}
                                  exchangeOptions={exchangeOptions}
                                  pipelines={pipelines}
                                  positions={positions}
                                  strategies={strategies}
                                  balances={balances}
                                  startPipeline={this.startPipeline}
                                  stopPipeline={this.stopPipeline}
                                  editPipeline={this.editPipeline}
                                  deletePipeline={this.deletePipeline}
                                  updateMessage={updateMessage}
                                  pipelinesMetrics={pipelinesMetrics}
                                  decimals={decimals}
                                  trades={trades}
                                  currentPrices={currentPrices}
                                  updateTrades={this.updateTrades}
                                />
                              )}/>
                            <Route path="/dashboard">
                                <Dashboard
                                  balances={balances}
                                  pipelines={pipelines}
                                  trades={trades}
                                  positions={positions}
                                  currentPrices={currentPrices}
                                  pipelinesMetrics={pipelinesMetrics}
                                  updatePipelinesMetrics={this.updatePipelinesMetrics}
                                />
                            </Route>
                            <Route path="/positions">
                                <PositionsPanel
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
