import {Fragment} from 'react'
import {Button, Icon} from "semantic-ui-react";
import {Pipeline, StartPipeline, StopPipeline} from "../types";


interface Props {
  pipeline: Pipeline
  startPipeline: StartPipeline
  stopPipeline: StopPipeline
}


function PipelineButton(props: Props) {

  const {
      startPipeline,
      stopPipeline,
      pipeline,
  } = props

  return (
      <Fragment>
        {pipeline.active ? (
          <Button
            onClick={() => stopPipeline(pipeline.id)}
            style={styles.button}
            color={'red'}
            icon
          >
            <span style={styles.icon}>
              <Icon name={'stop'}/>
            </span>
            Stop Bot
          </Button>
        ) : (
          <Button
              onClick={() => startPipeline({
                pipelineId: pipeline.id,
                name: pipeline.name,
                allocation: pipeline.allocation,
                symbol: pipeline.symbol,
                strategy: pipeline.strategy,
                candleSize: pipeline.candleSize,
                exchanges: pipeline.exchange,
                params: pipeline.params,
                paperTrading: pipeline.paperTrading,
                color: pipeline.color,
                leverage: pipeline.leverage,
              })}
              style={styles.button}
              color={'green'}
              icon
          >
            <span style={styles.icon}>
              <Icon name={'play'}/>
            </span>
            Start Bot
          </Button>
        )}
      </Fragment>
  );
}

export default PipelineButton;


const styles = {
  button: {
    width: '80%'
  },
  icon: {
    marginRight: '10px'
  }
}
