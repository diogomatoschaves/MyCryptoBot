import React, {useEffect, useReducer, useRef, useState} from "react";
import {Link} from 'react-router-dom'
import styled from 'styled-components'
import {Bot, Layers, PieChart, Radio, TestTube2} from 'lucide-react'
import {
  BalanceObj, EquityTimeSeries,
  PipelinesMetrics,
  PipelinesObject,
  Position,
  TradesObject,
  UpdatePipelinesMetrics
} from "../types";
import {COLORS, COLORS_ALT, GREEN, RED} from "../utils/constants";
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
import {Card, CardHeader, CardTitle, Stat, Tag} from "../ui";
import {theme} from "../theme";


const DashboardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  width: 100%;

  @media (max-width: 991px) {
    grid-template-columns: 1fr;
  }

  /* staggered entrance */
  & > * {
    animation: fadeUp 0.4s ease both;
  }
  & > *:nth-child(2) { animation-delay: 0.05s; }
  & > *:nth-child(3) { animation-delay: 0.1s; }
  & > *:nth-child(4) { animation-delay: 0.15s; }
  & > *:nth-child(5) { animation-delay: 0.2s; }
  & > *:nth-child(6) { animation-delay: 0.25s; }
`

const StatsRow = styled.div`
  display: flex;
  gap: 28px;
  flex-wrap: wrap;
  margin-bottom: 8px;
`

const PiesRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
`


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

  const { balances, pipelines, trades, positions, currentPrices, pipelinesMetrics: {
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
    .catch(() => {})
    updatePipelinesMetrics()
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trades, positions, pipelines, currentPrices, previous]);

  let totalPnl, pnlColor
  if (totalInitialEquity !== 0) {
    pnlColor = pnl > 0 ? GREEN : RED
    totalPnl = `${(pnl / totalInitialEquity * 100).toFixed(2)}%`
  } else {
    totalPnl = '—'
    pnlColor = theme.textDim
  }

  const positionsPieChartData = Object.keys(symbolsCount).map((symbol, index) => ({
    name: symbol,
    value: symbolsCount[symbol],
    color: COLORS[index % COLORS.length],
  }))

  const tradesPieChartData = tradesMetrics.tradesCount.map((entry, index) => {
    return {
      // @ts-ignore
      ...entry,
      color: COLORS_ALT[index % COLORS_ALT.length],
    }
  })

  const equityCards: Array<{key: 'live' | 'test'; label: string; icon: React.ReactNode; color: string}> = [
    {key: 'live', label: 'Live', icon: <Radio/>, color: theme.accent},
    {key: 'test', label: 'Testnet', icon: <TestTube2/>, color: theme.blue},
  ]

  return (
    <DashboardGrid>
      {equityCards.map(({key, label, icon, color}) => (
        <Card key={key}>
          <CardHeader>
            <CardTitle>
              {icon}
              Equity
            </CardTitle>
            <Tag color={color}>{label}</Tag>
          </CardHeader>
          <StatsRow>
            <Stat
              label="Total Equity"
              value={`${balances[key].USDT.totalBalance.toFixed(1)} USDT`}
              size="lg"
            />
            <Stat
              label="Available"
              value={`${balances[key].USDT.availableBalance.toFixed(1)} USDT`}
              size="lg"
              color={theme.textDim}
            />
          </StatsRow>
          <PortfolioChart dataProp={equityTimeSeries[key]} color={color}/>
        </Card>
      ))}
      <Card $interactive>
        <Link to="/pipelines">
          <CardHeader>
            <CardTitle>
              <Bot/>
              Trading Bots
            </CardTitle>
          </CardHeader>
          <StatsRow>
            <Stat label="# Bots" value={totalPipelines}/>
            <Stat label="# Active" value={activePipelines} color={GREEN}/>
            <Stat
              label="Best Win Rate"
              value={bestWinRate && bestWinRate.name ? (
                <TradingBotLabel pipelineId={bestWinRate.id} name={bestWinRate.name} color={bestWinRate.color}/>
              ) : '—'}
            />
            <Stat
              label="Most Trades"
              value={mostTrades && mostTrades.name ? (
                <TradingBotLabel pipelineId={mostTrades.id} name={mostTrades.name} color={mostTrades.color}/>
              ) : '—'}
            />
          </StatsRow>
        </Link>
      </Card>
      <TradesStats tradesMetrics={tradesMetrics}/>
      <Card $interactive>
        <Link to='/positions'>
          <CardHeader>
            <CardTitle>
              <Layers/>
              Positions
            </CardTitle>
          </CardHeader>
          <StatsRow>
            <Stat label="# Positions" value={openPositions}/>
            <Stat label="Total Size" value={`${totalEquityPositions.toFixed(1)} USDT`}/>
            <Stat label="Net Profit" value={totalPnl} color={pnlColor}/>
          </StatsRow>
        </Link>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>
            <PieChart/>
            Currencies
          </CardTitle>
        </CardHeader>
        <PiesRow>
          <CustomPieChart title={'Positions'} pieChartData={positionsPieChartData}/>
          <CustomPieChart title={'Trades'} pieChartData={tradesPieChartData}/>
        </PiesRow>
      </Card>
    </DashboardGrid>
  );
}


export default Dashboard;
