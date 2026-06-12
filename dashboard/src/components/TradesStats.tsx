import {Link} from 'react-router-dom'
import styled from 'styled-components'
import {ArrowLeftRight} from 'lucide-react'
import {timeFormatterDiff} from "../utils/helpers";
import {GREEN, RED} from "../utils/constants";
import {TradesMetrics} from "../types";
import {Card, CardHeader, CardTitle, Stat} from "../ui";


const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px 14px;

  @media (max-width: 480px) {
    grid-template-columns: repeat(2, 1fr);
  }
`

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

  const winRate = numberTrades > 0 ? (winningTrades / numberTrades) * 100 : null

  return (
    <Card style={style}>
      <Link to='/trades'>
        <CardHeader>
          <CardTitle>
            <ArrowLeftRight/>
            Trades
          </CardTitle>
        </CardHeader>
        <StatsGrid>
          <Stat label="# Trades" value={numberTrades}/>
          <Stat label="Max Duration" value={timeFormatterDiff(maxTradeDuration)}/>
          <Stat label="Avg Duration" value={timeFormatterDiff(avgTradeDuration)}/>
          <Stat
            label="Win Rate"
            value={winRate !== null ? `${winRate.toFixed(0)}%` : '—'}
            color={winRate === null ? undefined : winRate >= 50 ? GREEN : RED}
          />
          <Stat
            label="Best Trade"
            value={`${(bestTrade * 100).toFixed(2)}%`}
            color={bestTrade > 0 ? GREEN : RED}
          />
          <Stat
            label="Worst Trade"
            value={`${(worstTrade * 100).toFixed(2)}%`}
            color={worstTrade > 0 ? GREEN : RED}
          />
        </StatsGrid>
      </Link>
    </Card>
  )
}

export default TradesStats
