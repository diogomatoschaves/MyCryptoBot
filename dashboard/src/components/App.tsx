import '../App.css';
import {Component} from 'react'
import {Route, Switch, Redirect} from 'react-router-dom'
import {Location} from 'history'
import styled, {css} from 'styled-components'
import {
    ChangeMenu,
    DropdownOptions,
    MenuOption,
    PipelineParams,
    Position,
    StartPipeline,
    StopPipeline,
    GetCurrentPrices,
    Message,
    UpdateMessage,
    DeletePipeline,
    BalanceObj,
    Decimals,
    RawTrade,
    PipelinesMetrics,
    RawPipeline,
    PipelinesObject, TradesObject
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
    deleteBot, getPipelinesMetrics,
} from "../apiCalls";
import {RESOURCES_MAPPING} from "../utils/constants";
import Menu from "./Menu";
import MessageComponent from "./Message";
import PipelinePanel from "./PipelinePanel";
import TradesPanel from "./TradesPanel";
import {parseTrade, organizePositions, organizePipeline} from "../utils/helpers";
import PositionsPanel from "./PositionsPanel";
import {Box, StyledSegment, Wrapper} from "../styledComponents";
import Dashboard from "./Dashboard";
import {Grid, Header} from "semantic-ui-react";


const AppDiv = styled.div`
  text-align: center;
  width: 100vw;
  height: 100vh;
  position: absolute;
  justify-content: flex-start;
`

const StyledBox = styled(Box)`
  transition: bottom 1s ease;
  position: fixed;
  ${(props: any) =>
    props.bottom &&
    css`
      bottom: ${props.bottom}px;
    `}
`

const MenuColumn = styled.div`
    position: fixed;
    left: 0;
    bottom: 0;
    top: 0;
    width: 25vw;
`

const AppColumn = styled.div`
    position: absolute;
    left: 25vw;
    bottom: 0;
    top: 0;
    right: 0;
    // margin-left: 25vw;
    width: 75vw;
    height: 100vh;
    padding: 10px 50px;
    overflow: hidden
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
    message: Message
    pipelinesMetrics: PipelinesMetrics
}

interface Props {
    decimals: Decimals
    location: Location
    menuProperties: MenuOption[]
}


class App extends Component<Props, State> {

    messageTimeout: any

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
        message: {show: false, bottomProp: -300, text: null, color: "#000000", success: true},
        pipelinesMetrics: {
            totalPipelines: 0,
            activePipelines: 0,
            bestWinRate: {winRate: 0},
            mostTrades: {totalTrades: 0}
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

        this.updateTrades()

        this.updatePipelines()

        this.updatePositions()

        this.getAccountBalance()

        this.updatePipelinesMetrics()

        setInterval(() => {
            this.updateTrades()
        }, 60 * 1000)
    }

    componentDidUpdate(prevProps: Readonly<any>, prevState: Readonly<State>, snapshot?: any) {

        const { message, menuOption } = this.state

        if (prevState.message.show !== message.show && message.show) {
            this.setState({message: {...message, bottomProp: 40, show: false}})

            if (this.messageTimeout) {
                clearTimeout(this.messageTimeout)
            }
            this.messageTimeout = setTimeout(() => {
                this.setState((state) =>
                    ({
                        message: {
                            ...state.message,
                            bottomProp: -300
                        }
                    }),
                    () => {
                        if (this.messageTimeout) {
                            clearTimeout(this.messageTimeout)
                        }
                    }
                )
            }, 4200)
        }

        if (prevState.menuOption.code !== menuOption.code && menuOption.code === 'trades') {
            this.updateTrades()
            this.getCurrentPrices()
        }

        if (prevState.menuOption.code !== menuOption.code && menuOption.code === 'pipelines') {
            this.updatePipelines()
            this.getCurrentPrices()
        }

        if (prevState.menuOption.code !== menuOption.code && menuOption.code === 'positions') {
            this.updatePositions()
            this.getCurrentPrices()
        }
    }

    startPipeline: StartPipeline = (pipelineParams: PipelineParams) => {
        startBot(pipelineParams)
            .then(response => {
                this.setState(state => {
                    return {
                        message: {
                            ...state.message,
                            text: response.message,
                            show: true,
                            success: response.success,
                        },
                        pipelines: response.success ? {
                            ...state.pipelines,
                            [response.pipeline.id]: organizePipeline(response.pipeline)
                        } : state.pipelines
                    }
                })
            })
    }

    stopPipeline: StopPipeline = (pipelineId) => {
        return stopBot({pipelineId})
            .then(response => {
                this.setState(state => ({
                    message: {
                        ...state.message,
                        text: response.message,
                        show: true,
                        success: response.success
                    },
                    pipelines: response.success ? {
                        ...state.pipelines,
                        [pipelineId]: organizePipeline(response.pipeline)
                    } : state.pipelines
                }))
            })
    }

    deletePipeline: DeletePipeline = (pipelineId) => {
        deleteBot(pipelineId)
            .then(response => {
                this.setState(state => {
                    const {id, ...pipelines} = state.pipelines
                    return {
                        message: {
                        ...state.message,
                              text: response.message,
                              show: true,
                              success: response.success
                        },
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
    }

    changeMenu: ChangeMenu = (menuOption) => {
        this.setState({ menuOption })
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
        })
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
    }

    updatePipelinesMetrics = () => {
        getPipelinesMetrics()
          .then(response => {
              this.setState({
                  pipelinesMetrics: response
              })
          })
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
    }

    updateMessage: UpdateMessage = (text, success) => {
        this.setState(state => ({
            message: {
                ...state.message,
                show: true,
                text,
                success,
            }
        }))
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
            message,
            pipelinesMetrics
        } = this.state


        const { decimals, menuProperties, location } = this.props

        const menuOption = menuProperties.find(option => location.pathname.includes(option.code))

        return (
            <AppDiv className="flex-row">
                <MenuColumn>
                    <Menu menuOption={menuOption} changeMenu={this.changeMenu} menuProperties={menuProperties}/>
                </MenuColumn>
                <AppColumn>
                    <StyledSegment basic paddingTop="10px" padding="0" className="flex-column">
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
                            <Route path="/">
                                {/*<Wrapper>*/}
                                    <Switch>
                                        <Route path="/pipelines/:pipelineId?" render={({match}) => (
                                            <PipelinePanel
                                              match={match}
                                              symbolsOptions={symbolsOptions}
                                              strategiesOptions={strategiesOptions}
                                              candleSizeOptions={candleSizeOptions}
                                              exchangeOptions={exchangeOptions}
                                              pipelines={pipelines}
                                              strategies={strategies}
                                              balances={balances}
                                              startPipeline={this.startPipeline}
                                              stopPipeline={this.stopPipeline}
                                              deletePipeline={this.deletePipeline}
                                              updateMessage={this.updateMessage}
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
                                {/*</Wrapper>*/}
                            </Route>
                        </Switch>
                        {message.text && (
                          <StyledBox align="center" bottom={message.bottomProp}>
                              <MessageComponent success={message.success} message={message.text} color={message.color}/>
                          </StyledBox>
                        )}
                    </StyledSegment>
                </AppColumn>
            </AppDiv>
        );
    }
}


export default App;
