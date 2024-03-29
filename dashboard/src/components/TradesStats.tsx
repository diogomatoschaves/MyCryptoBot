import {Grid, Header, Segment} from "semantic-ui-react";
import {Link} from 'react-router-dom'
import {timeFormatterDiff} from "../utils/helpers";
import {GREEN, RED} from "../utils/constants";
import {TradesMetrics} from "../types";


interface Props {
  tradesMetrics: TradesMetrics
  style?: Object
}

const TradesStats = (props: Props) => {

  let { tradesMetrics } = props

  if (!tradesMetrics) {
    tradesMetrics = {
      winningTrades: 0,
      numberTrades: 0,
      maxTradeDuration: 0,
      avgTradeDuration: 0,
      bestTrade: 0,
      worstTrade: 0,
      losingTrades: 0
    }
  }

  const { winningTrades, numberTrades, maxTradeDuration, avgTradeDuration, bestTrade, worstTrade } = tradesMetrics;
  const { style } = props

  const winRate = winningTrades / numberTrades * 100

  return (
    <Segment secondary raised style={{...styles.rowSegment, ...(style && style)}}>
      <Link to='/trades'>
        <Header size={'medium'} color="purple">
          Trades
        </Header>
        <Grid columns={3} style={{height: '100%'}}>
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
              <Grid.Column style={{...styles.tradesColumn, color: bestTrade > 0 ? GREEN : RED}} >
                {(bestTrade * 100).toFixed(2)}%
              </Grid.Column>
            </Grid.Column>
            <Grid.Column>
              <Grid.Column style={styles.tradesHeader}>
                Worst Trade
              </Grid.Column>
              <Grid.Column style={{...styles.tradesColumn, color: worstTrade > 0 ? GREEN : RED}} >
                {(worstTrade * 100).toFixed(2)}%
              </Grid.Column>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Link>
    </Segment>
  )
}

export default TradesStats


const styles = {
  rowSegment: {
    // margin: '20px 10px',
    // width: '50%',
    minHeight: '200px'
  },
  tradesHeader: {
    fontSize: '1.0em',
    color: 'rgb(169,142,227)',
  },
  tradesColumn: {
    fontSize: '1.2em',
    color: '#6435C9',
    fontWeight: '600',
  },
}
