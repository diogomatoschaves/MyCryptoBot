import {Link} from 'react-router-dom'
import {Tag} from "../ui";
import {getBotColor} from "../theme";


interface Props {
  pipelineId?: number
  color?: string;
  name?: string
}


function TradingBotLabel(props: Props) {

  const { pipelineId, color, name } = props

  return (
    <Link
      to={`/pipelines/${pipelineId}`}
      onClick={(event) => event.stopPropagation()}
      style={{display: 'inline-flex', maxWidth: '100%'}}
    >
      <Tag color={getBotColor(color)} mono={false} maxWidth="140px" title={name}>
        {name}
      </Tag>
    </Link>
  )
}


export default TradingBotLabel;
