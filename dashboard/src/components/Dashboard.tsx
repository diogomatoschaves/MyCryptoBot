import {Grid, Header, Label, Segment} from "semantic-ui-react";
import {MenuOption, Position, Trade} from "../types";
import {StyledSegment} from "../styledComponents";
import {useEffect, useReducer, useRef} from "react";
import {timeFormatterDate, timeFormatterDiff} from "../utils/helpers";
import { PieChart } from 'react-minimal-pie-chart';
import {BLUE, DARK_YELLOW, GREEN, PINK, PURPLE, RED, TEAL, VIOLET, YELLOW} from "../utils/constants";


interface Props {
  menuOption: MenuOption
  trades: Trade[],
  positions: Position[],
  currentPrices: Object
}

const colorsArray = [PURPLE, VIOLET, PINK, BLUE, TEAL, GREEN, RED, YELLOW, DARK_YELLOW]
const UPDATE_TRADES_STATISTICS = 'UPDATE_TRADES_STATISTICS'
const UPDATE_POSITIONS_STATISTICS = 'UPDATE_POSITIONS_STATISTICS'


const tradesReducerCallback = (metrics: any, trade: Trade) => {
  return {
    numberTrades: metrics.numberTrades + 1,
    maxTradeDuration: trade.openTime < metrics.maxTradeDuration ? trade.openTime : metrics.maxTradeDuration,
    totalTradeDuration: trade.closeTime ? trade.closeTime.getTime() - trade.openTime.getTime()
        : new Date().getTime() - trade.openTime.getTime(),
    winningTrades: trade.profitLoss && trade.profitLoss > 0 ? metrics.winningTrades + 1 : metrics.winningTrades,
    closedTrades: trade.profitLoss ? metrics.closedTrades + 1 : metrics.closedTrades,
    bestTrade: metrics.bestTrade ? trade.profitLoss && trade.profitLoss > metrics.bestTrade
        ? trade.profitLoss : metrics.bestTrade : trade.profitLoss,
    worstTrade: metrics.worstTrade ? trade.profitLoss && trade.profitLoss < metrics.bestTrade
        ? trade.profitLoss : metrics.worstTrade : trade.profitLoss
  }
}

const tradesReducerInitialState = {
  numberTrades: 0,
  maxTradeDuration: 1E20,
  totalTradeDuration: 0,
  winningTrades: 0,
  closedTrades: 0,
  bestTrade: null,
  worstTrade: null
}

const tradesReducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_TRADES_STATISTICS:
      return {
        ...state,
        ...action.trades.reduce(tradesReducerCallback, tradesReducerInitialState),
      }
    default:
      throw new Error();
  }
}

const positionsReducerCallback = (currentPrices: Object) => (metrics: any, position: Position) => {
  return {
    openPositions: metrics.openPositions + 1,
    // @ts-ignore
    totalEquityPositions: metrics.totalEquityPositions + position.amount * currentPrices[position.symbol],
    totalInitialEquity: metrics.totalEquityPositions + position.amount * position.price,
    symbolsCount: {
      ...metrics.symbolsCount,
      [position.symbol]: metrics.symbolsCount[position.symbol] ? metrics.symbolsCount[position.symbol] + 1 : 1
    }
  }
}

const positionsReducerInitialState = {
  openPositions: 0,
  totalEquityPositions: 0,
  totalInitialEquity: 0,
  symbolsCount: {},
}

const positionsReducer = (state: any, action: any) => {
  switch (action.type) {
    case UPDATE_POSITIONS_STATISTICS:
      return {
        ...state,
        ...action.positions.reduce(positionsReducerCallback(action.currentPrices), positionsReducerInitialState),
      }
    default:
      throw new Error();
  }
}


function Dashboard(props: Props) {

  const { menuOption, trades, positions, currentPrices } = props

  const previous = useRef({trades, positions, currentPrices}).current;

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

  useEffect(() => {
    if (trades !== previous.trades) {
      tradesDispatch({
        type: UPDATE_TRADES_STATISTICS,
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
    return () => {
      previous.trades = trades
      previous.positions = positions
      previous.currentPrices = currentPrices
    };
  }, [trades, positions, currentPrices]);

  const avgTradeDuration = totalTradeDuration / numberTrades
  const winRate = winningTrades / closedTrades * 100

  const totalPnl = ((totalEquityPositions - totalInitialEquity) / totalInitialEquity * 100)
  const pnlColor = totalPnl > 0 ? GREEN : RED

  const pieChartData = Object.keys(symbolsCount).map((symbol, index) => ({
    title: symbol,
    value: (symbolsCount[symbol] / openPositions * 100),
    color: colorsArray[index],
  }))

  return (
      <StyledSegment basic className="flex-column">
        <Header size={'large'} dividing>
          <span style={{marginRight: 10}}>{menuOption.emoji}</span>
          {menuOption.text}
        </Header>
        <Segment secondary raised>
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
                  {timeFormatterDate(maxTradeDuration)}
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
        <Segment secondary raised style={{width: '70%'}}>
          <Header size={'medium'} color="pink">
            Open Positions
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
                  {totalPnl.toFixed(2)}%
                </Grid.Column>
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
            </Grid.Row>
          </Grid>
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
          />
        </Segment>
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
    tradesHeader: {
      fontSize: '1.0em',
      color: 'rgb(169,142,227)',
    },
    positionsHeader: {
      fontSize: '1.0em',
      color: 'rgb(184,126,206)',
    },
    tradesColumn: {
      fontSize: '1.4em',
      color: '#6435C9',
      fontWeight: '600',
    },
    positionsColumn: {
      fontSize: '1.4em',
      color: '#A333C8',
      fontWeight: '600',
    },
    buttonDiv: {
      width: '100%',
      alignSelf: 'center'
    }
  }
