import {Grid, Header, Label, Segment} from "semantic-ui-react";
import {MenuOption, Pipeline, Position, Trade} from "../types";
import {StyledSegment} from "../styledComponents";
import {useEffect, useReducer, useRef} from "react";
import {timeFormatterDate, timeFormatterDiff} from "../utils/helpers";
import {PieChart} from 'react-minimal-pie-chart';
import {COLORS, GREEN, RED} from "../utils/constants";
import {
  tradesReducer,
  tradesReducerCallback,
  tradesReducerInitialState,
  UPDATE_TRADES_STATISTICS
} from "../reducers/tradesReducer";
import {
  positionsReducer,
  positionsReducerCallback,
  positionsReducerInitialState,
  UPDATE_POSITIONS_STATISTICS
} from "../reducers/positionsReducer";
import {
  pipelinesReducer,
  pipelinesReducerCallback,
  pipelinesReducerInitialState,
  UPDATE_PIPELINES_STATISTICS
} from "../reducers/pipelinesReducer";


interface Props {
  menuOption: MenuOption,
  balances: Object,
  pipelines: Pipeline[],
  trades: Trade[],
  positions: Position[],
  currentPrices: Object
}


function Dashboard(props: Props) {

  const { menuOption, balances, pipelines, trades, positions, currentPrices } = props

  const previous = useRef({trades, positions, pipelines, currentPrices}).current;

  const [{
    numberTrades,
    maxTradeDuration,
    totalTradeDuration,
    winningTrades,
    closedTrades,
    bestTrade,
    worstTrade,
  }, tradesDispatch] = useReducer(
      tradesReducer, trades.reduce(tradesReducerCallback, tradesReducerInitialState),
  );

  const [{
    openPositions,
    totalEquityPositions,
    totalInitialEquity,
    symbolsCount,
  }, positionsDispatch] = useReducer(
      positionsReducer, positions.reduce(positionsReducerCallback(currentPrices), positionsReducerInitialState)
  );

  const [{
    totalPipelines,
    activePipelines,
    bestWinRate,
    mostTrades
  }, pipelinesDispatch] = useReducer(
    pipelinesReducer, pipelines.reduce(pipelinesReducerCallback(trades), pipelinesReducerInitialState)
  )

  useEffect(() => {
    if (trades !== previous.trades) {
      tradesDispatch({
        type: UPDATE_TRADES_STATISTICS,
        trades
      })

      pipelinesDispatch({
        type: UPDATE_PIPELINES_STATISTICS,
        pipelines,
        trades
      })
    }

    if (positions !== previous.positions || currentPrices !== previous.currentPrices) {
      positionsDispatch({
        type: UPDATE_POSITIONS_STATISTICS,
        positions,
        currentPrices
      })
    }

    if (pipelines != previous.pipelines) {
      pipelinesDispatch({
        type: UPDATE_PIPELINES_STATISTICS,
        pipelines,
        trades
      })
    }
    return () => {
      previous.trades = trades
      previous.positions = positions
      previous.pipelines = pipelines
      previous.currentPrices = currentPrices
    };
  }, [trades, positions, pipelines, currentPrices]);

  const avgTradeDuration = totalTradeDuration / numberTrades
  const winRate = winningTrades / closedTrades * 100

  let totalPnl, pnlColor
  if (totalInitialEquity !== 0) {
    totalPnl = ((totalEquityPositions - totalInitialEquity) / totalInitialEquity * 100)
    pnlColor = totalPnl > 0 ? GREEN : RED
    totalPnl = `${totalPnl.toFixed(2)}%`
  } else {
    totalPnl = '-'
    pnlColor = '#6435C9'
  }

  const pieChartData = Object.keys(symbolsCount).map((symbol, index) => ({
    title: symbol,
    value: (symbolsCount[symbol] / openPositions * 100),
    color: COLORS[index],
  }))


  return (
      <StyledSegment basic className="flex-column">
        <Header size={'large'} dividing>
          <span style={{marginRight: 10}}>{menuOption.emoji}</span>
          {menuOption.text}
        </Header>
        <Grid style={{width: '100%'}}>
          <Grid.Column style={{width: '100%'}} className="flex-column">
            <Grid.Row style={{width: '100%'}} className="flex-row">
              <Segment secondary raised style={styles.rowSegment}>
                <Header size={'medium'} color="blue">
                  Balance
                </Header>
                <Grid columns={3}>
                  {Object.keys(balances).map(account => (
                    <Grid.Row>
                      <Grid.Column style={styles.balanceTitle}>
                        <Label basic color='blue' size="large">
                          {account}
                        </Label>
                      </Grid.Column>
                      <Grid.Column>
                        <Grid.Column style={styles.balanceHeader}>
                          Total Equity
                        </Grid.Column>
                        <Grid.Column style={styles.balanceColumn} >
                          {/*@ts-ignore*/}
                          {`${balances[account].USDT.totalBalance.toFixed(1)} $USDT`}
                        </Grid.Column>
                      </Grid.Column>
                      <Grid.Column>
                        <Grid.Column style={styles.balanceHeader}>
                          Available Equity
                        </Grid.Column>
                        <Grid.Column style={styles.balanceColumn} >
                          {/*@ts-ignore*/}
                          {`${balances[account].USDT.availableBalance.toFixed(1)} $USDT`}
                        </Grid.Column>
                      </Grid.Column>
                    </Grid.Row>
                  ))}
                </Grid>
              </Segment>
              <Segment secondary raised style={styles.rowSegment}>
                <Header size={'medium'} color="purple">
                  Trading Bots
                </Header>
                <Grid columns={2}>
                  <Grid.Row>
                    <Grid.Column>
                      <Grid.Column style={styles.tradesHeader}>
                        # trading bots
                      </Grid.Column>
                      <Grid.Column style={styles.tradesColumn} >
                        {totalPipelines}
                      </Grid.Column>
                    </Grid.Column>
                    <Grid.Column>
                      <Grid.Column floated='left' style={styles.tradesHeader}>
                        # active trading bots
                      </Grid.Column>
                      <Grid.Column floated='right' style={styles.tradesColumn}>
                        {activePipelines}
                      </Grid.Column>
                    </Grid.Column>
                  </Grid.Row>
                  <Grid.Row>
                    <Grid.Column>
                      <Grid.Column floated='left' style={styles.tradesHeader}>
                        Best Win Rate
                      </Grid.Column>
                      <Grid.Column floated='right' style={styles.tradesColumn} >
                        <Label color={bestWinRate.color}>{bestWinRate.name}</Label>
                      </Grid.Column>
                    </Grid.Column>
                    <Grid.Column>
                      <Grid.Column style={styles.tradesHeader}>
                        Most Trades
                      </Grid.Column>
                      <Grid.Column style={styles.tradesColumn}>
                        <Label color={mostTrades.color}>{mostTrades.name}</Label>
                      </Grid.Column>
                    </Grid.Column>
                  </Grid.Row>
                </Grid>
              </Segment>
            </Grid.Row>
            <Grid.Row style={{width: '100%'}} className="flex-row">
              <Segment secondary raised style={{...styles.rowSegment}}>
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
                        Total Equity
                      </Grid.Column>
                      <Grid.Column floated='right' style={styles.positionsColumn} >
                        {totalEquityPositions.toFixed(0)} USDT
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
                {positions.length > 0 &&
                <PieChart
                  viewBoxSize={[100, 65]}
                  center={[50, 25]}
                  data={pieChartData}
                  label={({dataEntry}) => `${dataEntry.title}`}
                  labelStyle={(index) => ({
                    fill: pieChartData[index].color,
                    fontSize: '3px',
                    fontFamily: 'sans-serif',
                  })}
                  lineWidth={65}
                  radius={27}
                  labelPosition={110}
                />}
              </Segment>
              <Segment secondary raised style={styles.rowSegment}>
                <Header size={'medium'} color="purple">
                  Trades
                </Header>
                <Grid columns={3}>
                  <Grid.Row>
                    <Grid.Column>
                      <Grid.Column style={styles.tradesHeader}>
                        # trades
                      </Grid.Column>
                      <Grid.Column style={styles.tradesColumn} >
                        {numberTrades}
                      </Grid.Column>
                    </Grid.Column>
                    <Grid.Column>
                      <Grid.Column floated='left' style={styles.tradesHeader}>
                        Max trade duration
                      </Grid.Column>
                      <Grid.Column floated='right' style={styles.tradesColumn}>
                        {timeFormatterDiff(maxTradeDuration)}
                      </Grid.Column>
                    </Grid.Column>
                    <Grid.Column>
                      <Grid.Column floated='left' style={styles.tradesHeader}>
                        Avg trade duration
                      </Grid.Column>
                      <Grid.Column floated='right' style={styles.tradesColumn} >
                        {timeFormatterDiff(avgTradeDuration)}
                      </Grid.Column>
                    </Grid.Column>
                  </Grid.Row>
                  <Grid.Row>
                    <Grid.Column>
                      <Grid.Column style={styles.tradesHeader}>
                        Win Rate
                      </Grid.Column>
                      <Grid.Column style={styles.tradesColumn} >
                        {winRate.toFixed(0)}%
                      </Grid.Column>
                    </Grid.Column>
                    <Grid.Column>
                      <Grid.Column style={styles.tradesHeader}>
                        Best Trade
                      </Grid.Column>
                      <Grid.Column style={styles.tradesColumn} >
                        {(bestTrade * 100).toFixed(2)}%
                      </Grid.Column>
                    </Grid.Column>
                    <Grid.Column>
                      <Grid.Column style={styles.tradesHeader}>
                        Worst Trade
                      </Grid.Column>
                      <Grid.Column style={styles.tradesColumn} >
                        {(worstTrade * 100).toFixed(2)}%
                      </Grid.Column>
                    </Grid.Column>
                  </Grid.Row>
                </Grid>
              </Segment>
            </Grid.Row>
          </Grid.Column>
        </Grid>
      </StyledSegment>
  );
}


export default Dashboard;

const styles = {
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
      width: '50%',
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
      color: 'rgb(184,126,206)',
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
      color: '#A333C8',
      fontWeight: '600',
    },
    buttonDiv: {
      width: '100%',
      alignSelf: 'center'
    }
  }
