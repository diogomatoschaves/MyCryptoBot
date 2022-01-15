import React from 'react';
import {Divider, Table} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {MenuOption, Position} from "../types";
import PositionRow from "./PositionRow";


interface Props {
  menuOption: MenuOption;
  positions: Position[]
}

const PositionsPanel = (props: Props) => {

  const { menuOption, positions } = props

  return (
      <StyledSegment basic className="flex-column">
        <Divider horizontal style={{marginBottom: '20px', marginTop: '0'}}>
          <span>{menuOption.emoji}</span> {menuOption.text}
        </Divider>
        <Table basic='very'>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>Symbol</Table.HeaderCell>
              <Table.HeaderCell>Exchange</Table.HeaderCell>
              <Table.HeaderCell>Status</Table.HeaderCell>
              <Table.HeaderCell>Position</Table.HeaderCell>
              <Table.HeaderCell>Amount</Table.HeaderCell>
              <Table.HeaderCell>Price</Table.HeaderCell>
              <Table.HeaderCell>Age</Table.HeaderCell>
              <Table.HeaderCell>Paper Trading</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {positions.map((position, index) => {
              return <PositionRow index={index} position={position}/>
            })}
          </Table.Body>
        </Table>
      </StyledSegment>
  );
};

export default PositionsPanel;