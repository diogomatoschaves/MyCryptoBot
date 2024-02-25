import React, {useEffect, useState, Fragment} from 'react';
import {XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart} from 'recharts';
import {getEquityTimeSeries} from "../apiCalls";
import {Data} from "../types";
import {convertDate} from "../utils/helpers";

interface Props {
  pipelineId?: string
  dataProp?: Data[]
  width?: string
}

const formatYAxis = (tick: string) => {
  return `${tick} USDT`
}

const PortfolioChart = (props: Props) => {

  const { pipelineId, dataProp, width } = props

  const [data, setData] = useState([])

  const fetchEquityData = (pipelineId: string) => {
    getEquityTimeSeries({pipelineId, maxItems: 500})
      .then((response) => {
        if (response.success) {
          setData(response.data)
        }
      })
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

  return (
      <Fragment>
        {data.length > 0 && (
          <ResponsiveContainer width={width ? width : "97%"} height={180}>
            <AreaChart
              data={data}
              margin={{
                top: 30,
                right: 0,
                left: 5,
                bottom: 0,
              }}
            >
              <XAxis dataKey="time" hide tickFormatter={convertDate}/>
              <YAxis tickFormatter={formatYAxis}/>
              <Tooltip labelFormatter={convertDate}/>
              <Area type="monotone" dataKey="$" stroke="#8884d8" fill="#8884d8" strokeWidth={1.5} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </Fragment>
  );
};

export default PortfolioChart;
