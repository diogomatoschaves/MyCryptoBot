import {Divider} from "semantic-ui-react";
import {MenuOption} from "../types";
import {StyledSegment} from "../styledComponents";


interface Props {
  menuOption: MenuOption
}


function Dashboard(props: Props) {

  const { menuOption } = props

  return (
      <StyledSegment basic className="flex-column">
        <Divider horizontal style={{marginBottom: '20px', marginTop: '0'}}>
          <span>{menuOption.emoji}</span> {menuOption.text}
        </Divider>
      </StyledSegment>
  );
}

export default Dashboard;
