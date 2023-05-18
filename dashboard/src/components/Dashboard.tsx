import {Grid, Header, Label, Segment} from "semantic-ui-react";
import {
  BalanceObj, EquityTimeSeries,
  PipelinesMetrics,
  PipelinesObject,
  Position,
  TradesObject,
  UpdatePipelinesMetrics
} from "../types";
import {StyledSegment} from "../styledComponents";
import {useEffect, useReducer, useRef, useState} from "react";
import {COLORS, COLORS_ALT, GREEN, RED} from "../utils/constants";
import {Link} from 'react-router-dom'
import {
  positionsReducer,
  positionsReducerCallback,
  positionsReducerInitialState,
  UPDATE_POSITIONS_STATISTICS
} from "../reducers/positionsReducer";
import {getTradesMetrics} from "../apiCalls";
import TradesStats from "./TradesStats";
import PortfolioChart from "./PortfolioChart";
import TradingBotLabel from "./TradingBotLabel";
import CustomPieChart from "./CustomPieChart";


interface Props {
  size: string
  balances: BalanceObj,
  pipelines: PipelinesObject,
  trades: TradesObject,
  positions: Position[],
  currentPrices: Object
  pipelinesMetrics: PipelinesMetrics
  equityTimeSeries: EquityTimeSeries
  updatePipelinesMetrics: UpdatePipelinesMetrics
}


function Dashboard(props: Props) {

  const { size, balances, pipelines, trades, positions, currentPrices, pipelinesMetrics: {
    totalPipelines,
    activePipelines,
    bestWinRate,
    mostTrades}, updatePipelinesMetrics, equityTimeSeries} = props

  const previous = useRef({trades, positions, pipelines, currentPrices}).current;

  const [{
    openPositions,
    totalEquityPositions,
    totalInitialEquity,
    pnl,
    symbolsCount,
  }, positionsDispatch] = useReducer(
      positionsReducer, positions.reduce(positionsReducerCallback(currentPrices), positionsReducerInitialState)
  );

  const [tradesMetrics, setTradesMetrics] = useState({
    numberTrades: 0,
    maxTradeDuration: 0,
    avgTradeDuration: 0,
    winningTrades: 0,
    losingTrades: 0,
    bestTrade: 0,
    worstTrade: 0,
    tradesCount: []
  })

  const fetchTradesData = async () => {
    const tradesMetrics = await getTradesMetrics()
    setTradesMetrics(tradesMetrics)
  }

  useEffect(() =>{
    fetchTradesData()
    updatePipelinesMetrics()
  }, [])

  useEffect(() => {
    if (trades !== previous.trades) {
      fetchTradesData()
      updatePipelinesMetrics()
    }

    if (positions !== previous.positions || currentPrices !== previous.currentPrices) {
      positionsDispatch({
        type: UPDATE_POSITIONS_STATISTICS,
        positions,
        currentPrices
      })
    }

    if (pipelines !== previous.pipelines) {
      updatePipelinesMetrics()
    }
    return () => {
      previous.trades = trades
      previous.positions = positions
      previous.pipelines = pipelines
      previous.currentPrices = currentPrices
    };
  }, [trades, positions, pipelines, currentPrices]);

  let totalPnl, pnlColor
  if (totalInitialEquity !== 0) {
    pnlColor = pnl > 0 ? GREEN : RED
    totalPnl = `${(pnl / totalInitialEquity * 100).toFixed(2)}%`
  } else {
    totalPnl = '-'
    pnlColor = '#6435C9'
  }

  const positionsPieChartData = Object.keys(symbolsCount).map((symbol, index) => ({
    name: symbol,
    value: symbolsCount[symbol],
    color: COLORS[index],
  }))

  const tradesPieChartData = tradesMetrics.tradesCount.map((entry, index) => {
    return {
      // @ts-ignore
      ...entry,
      color: COLORS_ALT[index],
    }
  })

  const isMobile = ['mobile'].includes(size)

  const rowStyle = {
    width: '100%',
    paddingBottom: isMobile ? 0 : '3px',
    paddingTop: isMobile ? 0 : '3px'
  }

  return (
      <StyledSegment basic className="flex-column">
        <Grid style={{width: '100%'}} className="flex-column">
              <Grid.Row style={rowStyle} className="flex-row">
              <Segment secondary raised style={{...styles.rowSegment, width: isMobile ? '100%' : '44%'}}>
                <Header size={'medium'} color="blue">
                  Equity
                  <Label basic color='blue' >
                    {'live'}
                  </Label>
                </Header>
                <Grid columns={2}>
                  <Grid.Row>
                    <Grid.Column>
                      <Grid.Column style={styles.balanceHeader}>
                        Total Equity
                      </Grid.Column>
                      <Grid.Column style={styles.balanceColumn} >
                        {/*@ts-ignore*/}
                        {`${balances.live.USDT.totalBalance.toFixed(1)} $USDT`}
                      </Grid.Column>
                    </Grid.Column>
                    <Grid.Column>
                      <Grid.Column style={styles.balanceHeader}>
                        Available Equity
                      </Grid.Column>
                      <Grid.Column style={styles.balanceColumn} >
                        {/*@ts-ignore*/}
                        {`${balances.live.USDT.availableBalance.toFixed(1)} $USDT`}
                      </Grid.Column>
                    </Grid.Column>
                  </Grid.Row>
                </Grid>
                <PortfolioChart dataProp={equityTimeSeries.live}/>
              </Segment>
              <Segment secondary raised style={{...styles.rowSegment, width: isMobile ? '100%' : '44%'}}>
                <Header size={'medium'} color="blue">
                  Equity
                  <Label basic color='blue' >
                    {'test'}
                  </Label>
                </Header>
                <Grid columns={2}>
                  <Grid.Row>
                    <Grid.Column>
                      <Grid.Column style={styles.balanceHeader}>
                        Total Equity
                      </Grid.Column>
                      <Grid.Column style={styles.balanceColumn} >
                        {/*@ts-ignore*/}
                        {`${balances.test.USDT.totalBalance.toFixed(1)} $USDT`}
                      </Grid.Column>
                    </Grid.Column>
                    <Grid.Column>
                      <Grid.Column style={styles.balanceHeader}>
                        Available Equity
                      </Grid.Column>
                      <Grid.Column style={styles.balanceColumn} >
                        {/*@ts-ignore*/}
                        {`${balances.test.USDT.availableBalance.toFixed(1)} $USDT`}
                      </Grid.Column>
                    </Grid.Column>
                  </Grid.Row>
                </Grid>
                <PortfolioChart dataProp={equityTimeSeries.test}/>
              </Segment>
            </Grid.Row>
            <Grid.Row style={rowStyle} className="flex-row">
              <Segment secondary raised style={{...styles.rowSegment, width: isMobile ? '100%' : '44%'}}>
                <Link to="/pipelines">
                  <Header size={'medium'} color="teal">
                    Trading Bots
                  </Header>
                  <Grid columns={2}>
                    <Grid.Row>
                      <Grid.Column>
                        <Grid.Column style={styles.pipelinesHeader}>
                          # trading bots
                        </Grid.Column>
                        <Grid.Column style={styles.pipelinesColumn} >
                          {totalPipelines}
                        </Grid.Column>
                      </Grid.Column>
                      <Grid.Column>
                        <Grid.Column floated='left' style={styles.pipelinesHeader}>
                          # active trading bots
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.pipelinesColumn}>
                          {activePipelines}
                        </Grid.Column>
                      </Grid.Column>
                    </Grid.Row>
                    <Grid.Row>
                      <Grid.Column>
                        <Grid.Column floated='left' style={styles.pipelinesHeader}>
                          Best Win Rate
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.pipelinesColumn}>
                          {bestWinRate && <TradingBotLabel pipelineId={bestWinRate.id} name={bestWinRate.name} color={bestWinRate.color}/>}
                        </Grid.Column>
                      </Grid.Column>
                      <Grid.Column>
                        <Grid.Column style={styles.pipelinesHeader}>
                          Most Trades
                        </Grid.Column>
                        <Grid.Column style={styles.pipelinesColumn}>
                          {mostTrades && <TradingBotLabel pipelineId={mostTrades.id} name={mostTrades.name} color={mostTrades.color}/>}
                        </Grid.Column>
                      </Grid.Column>
                    </Grid.Row>
                  </Grid>
                </Link>
              </Segment>
              <TradesStats tradesMetrics={tradesMetrics} style={{...styles.tradesStatsStyle , width: isMobile ? '100%' : '44%'}}/>
            </Grid.Row>
            <Grid.Row style={rowStyle} className="flex-row">
              <Segment secondary raised style={{...styles.rowSegment, minHeight: '245px', width: isMobile ? '100%' : '44%'}}>
                <Link to='/positions'>
                  <Header size={'medium'} color="pink">
                    Positions
                  </Header>
                  <Grid columns={3}>
                    <Grid.Row>
                      <Grid.Column>
                        <Grid.Column style={styles.positionsHeader}>
                          # positions
                        </Grid.Column>
                        <Grid.Column style={styles.positionsColumn} >
                          {openPositions}
                        </Grid.Column>
                      </Grid.Column>
                      <Grid.Column>
                        <Grid.Column floated='left' style={styles.positionsHeader}>
                          Total Size
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.positionsColumn} >
                          {totalEquityPositions.toFixed(1)} USDT
                        </Grid.Column>
                      </Grid.Column>
                      <Grid.Column>
                        <Grid.Column floated='left' style={styles.positionsHeader}>
                          Net profit
                        </Grid.Column>
                        <Grid.Column floated='right' style={{...styles.positionsColumn, color: pnlColor}} >
                          {totalPnl}
                        </Grid.Column>
                      </Grid.Column>
                    </Grid.Row>
                    <Grid.Row>
                    </Grid.Row>
                  </Grid>
                </Link>
              </Segment>
              <Segment secondary raised style={{...styles.rowSegment, width: isMobile ? '100%' : '44%'}}>
                <Header size={'medium'} color="pink">
                  Currencies
                </Header>
                <Grid>
                  <Grid.Row columns={2}>
                    <Grid.Column>
                      <CustomPieChart title={'Positions'} pieChartData={positionsPieChartData}/>
                    </Grid.Column>
                    <Grid.Column>
                      <CustomPieChart title={'Trades'} pieChartData={tradesPieChartData}/>
                    </Grid.Column>
                  </Grid.Row>
                </Grid>
              </Segment>
            </Grid.Row>
        </Grid>
      </StyledSegment>
  );
}


export default Dashboard;

const styles = {
    tradesStatsStyle: {
      margin: '20px 10px',
      width: '50%',
    },
    segment: {
      width: '80%',
      padding: '30px 30px 20px',
      marginBottom: '40px'
    },
    balanceTitle: {
      alignSelf: 'center'
    },
    rowSegment: {
      margin: '20px 10px',
      minHeight: '200px'
    },
    balanceHeader: {
      fontSize: '1.0em',
      color: 'rgb(119,137,220)',
    },
    tradesHeader: {
      fontSize: '1.0em',
      color: 'rgb(169,142,227)',
    },
    positionsHeader: {
      fontSize: '1.0em',
      color: 'rgb(198,104,206)',
    },
    pipelinesHeader: {
      fontSize: '1.0em',
      color: 'rgb(94,182,182)'
    },
    balanceColumn: {
      fontSize: '1.2em',
      color: '#3555c9',
      fontWeight: '600',
    },
    tradesColumn: {
      fontSize: '1.2em',
      color: '#6435C9',
      fontWeight: '600',
    },
    positionsColumn: {
      fontSize: '1.2em',
      color: '#9235ad',
      fontWeight: '600',
    },
    pipelinesColumn: {
      fontSize: '1.2em',
      color: '#0e6972',
      fontWeight: '600',
    },
    buttonDiv: {
      width: '100%',
      alignSelf: 'center'
    }
  }
