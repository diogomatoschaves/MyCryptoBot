import React, {useEffect, useState, Fragment} from 'react';
import {XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart} from 'recharts';
import {pipelineEquity} from "../apiCalls";

const data1 = [
  { time: '2022-01-01', $: 1000 },
  { time: '2022-02-01', $: 1200 },
  { time: '2022-03-01', $: 900 },
  { time: '2022-04-01', $: 1100 },
  { time: '2022-05-01', $: 1300 },
  { time: '2022-06-01', $: 1500 },
];

interface Props {
  pipelineId: string
}

const convertDate = (timeStamp: number) => {
  return new Date(timeStamp).toISOString();
}


const PortfolioChart = (props: Props) => {

  const { pipelineId } = props

  const [data, setData] = useState([])

  const fetchEquityData = (pipelineId: string) => {
    pipelineEquity({pipelineId, timeFrame: null})
      .then((response) => {
        if (response.success) {
          setData(response.data.map((entry: any) => {
            return {
              ...entry,
              time: convertDate(entry.time)
            }
          }))
        }
      })
  }

  useEffect(() => {
    fetchEquityData(pipelineId)
  }, [])

  return (
      <Fragment>
        {data.length > 0 && (
          <ResponsiveContainer width="97%" height={200}>
            <AreaChart
              width={200}
              height={80}
              data={data}
              margin={{
                top: 5,
                right: 0,
                left: 0,
                bottom: 5,
              }}
            >
              <XAxis dataKey="time" hide/>
              <YAxis hide />
              <Tooltip />
              <Area type="monotone" dataKey="$" stroke="#8884d8" fill="#8884d8" strokeWidth={1.5} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </Fragment>
  );
};

export default PortfolioChart;
