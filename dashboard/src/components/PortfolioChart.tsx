import {useEffect, useState} from 'react';
import {XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart, CartesianGrid} from 'recharts';
import {getEquityTimeSeries} from "../apiCalls";
import {Data} from "../types";
import {convertDate} from "../utils/helpers";
import {theme} from "../theme";

interface Props {
  pipelineId?: string
  dataProp?: Data[]
  height?: number
  color?: string
}

const formatYAxis = (tick: number) => {
  if (Math.abs(tick) >= 1000) return `${(tick / 1000).toFixed(1)}k`
  return String(tick)
}

const tooltipStyles = {
  contentStyle: {
    background: theme.bgElevated,
    border: `1px solid ${theme.borderStrong}`,
    borderRadius: 8,
    fontFamily: theme.fontMono,
    fontSize: 12,
    color: theme.text,
  },
  labelStyle: {color: theme.textDim, marginBottom: 4},
  itemStyle: {color: theme.accent},
}

const PortfolioChart = (props: Props) => {

  const { pipelineId, dataProp, height, color } = props

  const [data, setData] = useState([])

  const strokeColor = color || theme.accent

  const fetchEquityData = (pipelineId: string) => {
    getEquityTimeSeries({pipelineId, maxItems: 500})
      .then((response) => {
        if (response.success) {
          setData(response.data)
        }
      })
      .catch(() => {})
  }

  useEffect(() => {
    if (pipelineId) {
      fetchEquityData(pipelineId)
    } else if (dataProp){
      // @ts-ignore
      setData(dataProp)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataProp])

  if (data.length === 0) return null

  const gradientId = `equityFill-${pipelineId || 'main'}-${strokeColor.replace('#', '')}`

  return (
    <ResponsiveContainer width="100%" height={height || 180}>
      <AreaChart
        data={data}
        margin={{
          top: 10,
          right: 4,
          left: 0,
          bottom: 0,
        }}
      >
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={strokeColor} stopOpacity={0.28}/>
            <stop offset="100%" stopColor={strokeColor} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid stroke={theme.border} strokeDasharray="3 6" vertical={false}/>
        <XAxis dataKey="time" hide tickFormatter={convertDate}/>
        <YAxis
          tickFormatter={formatYAxis}
          width={46}
          tick={{fill: theme.textFaint, fontFamily: theme.fontMono, fontSize: 11}}
          axisLine={false}
          tickLine={false}
          domain={['auto', 'auto']}
        />
        <Tooltip
          labelFormatter={convertDate}
          formatter={(value: any) => [`${Number(value).toFixed(2)} USDT`, 'Equity']}
          {...tooltipStyles}
        />
        <Area
          type="monotone"
          dataKey="$"
          stroke={strokeColor}
          strokeWidth={1.8}
          fill={`url(#${gradientId})`}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default PortfolioChart;
