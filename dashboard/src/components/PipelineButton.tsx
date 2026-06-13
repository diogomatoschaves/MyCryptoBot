import {useState} from 'react'
import {Play, Square} from 'lucide-react'
import {Pipeline, StartPipeline, StopPipeline} from "../types";
import {Button} from "../ui";


interface Props {
  pipeline: Pipeline
  startPipeline: StartPipeline
  stopPipeline: StopPipeline
  fullWidth?: boolean
}


function PipelineButton(props: Props) {

  const {
      startPipeline,
      stopPipeline,
      pipeline,
      fullWidth = true,
  } = props

  const [loading, setLoading] = useState(false)

  return pipeline.active ? (
    <Button
      variant="danger"
      icon={<Square/>}
      fullWidth={fullWidth}
      loading={loading}
      onClick={(event) => {
        setLoading(true)
        event.preventDefault();
        event.stopPropagation()
        stopPipeline(pipeline.id).then(() => setLoading(false))
      }}
    >
      Stop Bot
    </Button>
  ) : (
    <Button
      variant="success"
      icon={<Play/>}
      fullWidth={fullWidth}
      loading={loading}
      onClick={(event) => {
        setLoading(true)
        event.preventDefault();
        event.stopPropagation()
        startPipeline({
            pipelineId: pipeline.id,
            name: pipeline.name,
            equity: pipeline.initialEquity,
            symbol: pipeline.symbol,
            strategy: pipeline.strategy,
            candleSize: pipeline.candleSize,
            exchanges: pipeline.exchange,
            paperTrading: pipeline.paperTrading,
            color: pipeline.color,
            leverage: pipeline.leverage,
        }).then(() => setLoading(false))
      }}
    >
      Start Bot
    </Button>
  );
}

export default PipelineButton;
