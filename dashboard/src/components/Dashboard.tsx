import {Divider, Header, Label, Segment, Statistic} from "semantic-ui-react";
import {MenuOption} from "../types";
import {StyledSegment} from "../styledComponents";


interface Props {
  menuOption: MenuOption
}


function Dashboard(props: Props) {

  const { menuOption } = props

  return (
      <StyledSegment basic className="flex-column">
        <Header size={'large'} dividing>
          <span style={{marginRight: 10}}>{menuOption.emoji}</span>
          {menuOption.text}
        </Header>
        <Segment>
          <Statistic>
            <Statistic.Label># Trades</Statistic.Label>
            <Statistic.Value>40</Statistic.Value>
          </Statistic>
        </Segment>
      </StyledSegment>
  );
}

export default Dashboard;
