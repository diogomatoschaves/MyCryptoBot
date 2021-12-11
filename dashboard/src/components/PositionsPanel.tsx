import React from 'react';
import {Divider} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {MenuOption,} from "../types";


interface Props {
  menuOption: MenuOption;
}

const PositionsPanel = (props: Props) => {

  const { menuOption } = props

  return (
      <StyledSegment basic className="flex-column">
        <Divider horizontal style={{marginBottom: '20px', marginTop: '0'}}>
          <span>{menuOption.emoji}</span> {menuOption.text}
        </Divider>
      </StyledSegment>
  );
};

export default PositionsPanel;