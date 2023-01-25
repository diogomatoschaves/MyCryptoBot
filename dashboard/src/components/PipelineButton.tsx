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
      <div style={styles.buttonDiv} className='flex-column'>
        {pipeline.active ? (
          <Button
            onClick={(event) => {
                event.preventDefault();
                event.stopPropagation()
                stopPipeline(pipeline.id)
            }}
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
              onClick={(event) => {
                  event.preventDefault();
                  event.stopPropagation()
                  startPipeline({
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
                  })
              }}
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
      </div>
  );
}

export default PipelineButton;


const styles = {
    buttonDiv: {
        width: '100%',
        alignSelf: 'center'
    },
    button: {
        width: '80%'
    },
    icon: {
        marginRight: '10px'
    }
}
