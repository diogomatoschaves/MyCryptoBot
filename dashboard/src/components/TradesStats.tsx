import {Grid, Header, Segment} from "semantic-ui-react";
import {timeFormatterDiff} from "../utils/helpers";
import {GREEN, RED} from "../utils/constants";
import {TradesMetrics} from "../types";


interface Props {
  tradesMetrics: TradesMetrics
}

const TradesStats = (props: Props) => {

  if (!props.tradesMetrics) return <div></div>

  const { winningTrades, numberTrades, maxTradeDuration, avgTradeDuration, bestTrade, worstTrade } = props.tradesMetrics;

  const winRate = winningTrades / numberTrades * 100

  return (
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
