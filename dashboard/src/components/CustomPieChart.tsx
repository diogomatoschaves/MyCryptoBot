import {Tooltip, ResponsiveContainer, PieChart, Pie, Cell} from 'recharts';
import styled from 'styled-components';
import {PieChartData} from "../types";
import {theme} from "../theme";


const ChartWrap = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 0;
`

const ChartTitle = styled.span`
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-faint);
`

const LegendWrap = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px 12px;
`

const LegendItem = styled.span<{$color: string}>`
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-dim);

  &::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 2px;
    background: ${({$color}) => $color};
  }
`

const Empty = styled.div`
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-faint);
`

interface Props {
  title: string
  pieChartData?: PieChartData[]
}

const RADIAN = Math.PI / 180;

// @ts-ignore
const renderCustomizedLabel = ({ cx, cy, midAngle, outerRadius, percent }) => {
  const radius = outerRadius * 1.22;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text
      x={x}
      y={y}
      fill={theme.textDim}
      fontFamily={theme.fontMono}
      fontSize={10}
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};


const CustomPieChart = (props: Props) => {
  const { title, pieChartData } = props

  const hasData = pieChartData && pieChartData.length > 0

  return (
    <ChartWrap>
      <ChartTitle>{title}</ChartTitle>
      {hasData ? (
        <ResponsiveContainer width="100%" height={150}>
          <PieChart>
            <Pie
              data={pieChartData}
              dataKey="value"
              nameKey="name"
              innerRadius={36}
              outerRadius={50}
              paddingAngle={4}
              stroke="none"
              labelLine={false}
              label={renderCustomizedLabel}
            >
              {pieChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color}/>
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: theme.bgElevated,
                border: `1px solid ${theme.borderStrong}`,
                borderRadius: 8,
                fontFamily: theme.fontMono,
                fontSize: 12,
              }}
              itemStyle={{color: theme.text}}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <Empty>No data</Empty>
      )}
      {hasData && (
        <LegendWrap>
          {pieChartData.map((entry, index) => (
            <LegendItem key={index} $color={entry.color}>
              {entry.name}
            </LegendItem>
          ))}
        </LegendWrap>
      )}
    </ChartWrap>
  );
};

export default CustomPieChart;
