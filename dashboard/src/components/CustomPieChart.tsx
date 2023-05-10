import React, {Fragment} from 'react';
import {Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend} from 'recharts';
import {PieChartData} from "../types";


interface Props {
  title: string
  pieChartData?: PieChartData[]
}

const RADIAN = Math.PI / 180;

// @ts-ignore
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
  const radius = outerRadius * 1.1;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text x={x} y={y} fill="black" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};


const CustomPieChart = (props: Props) => {
  const { title, pieChartData } = props

  return (
    <Fragment>
      <text fill="black" textAnchor="middle" dominantBaseline="central">
        <tspan fontSize="14">{title}</tspan>
      </text>
      {pieChartData && pieChartData.length > 0 && (
        <ResponsiveContainer width="97%" height={160}>
          <PieChart >
            <Pie
              data={pieChartData}
              dataKey="value"
              nameKey="name"
              innerRadius={40}
              outerRadius={55}
              fill='#E03997'
              paddingAngle={5}
              labelLine={false}
              label={renderCustomizedLabel}
            >
              {pieChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Legend />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      )}
    </Fragment>
  );
};

export default CustomPieChart;
