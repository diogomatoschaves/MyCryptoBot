import {Label} from "semantic-ui-react";
import {Link} from 'react-router-dom'


interface Props {
  pipelineId?: number
  color?: string;
  name?: string
}


function TradingBotLabel(props: Props) {

  const { pipelineId, color, name, } = props

  return (
    <Link to={`/pipelines/${pipelineId}`}>
      {/*// @ts-ignore*/}
      <Label color={color}>
        {/*// @ts-ignore*/}
        <span style={styles.labelStyle}>
          {name}
        </span>
      </Label>
    </Link>
  )
}


export default TradingBotLabel;

const styles = {
  labelStyle: {
    display: 'inline-block',
    maxWidth: '90px',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  }
}