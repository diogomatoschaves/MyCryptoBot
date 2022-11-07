import React from 'react';
import {Header, Table} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {Decimals, MenuOption, Pipeline, Position} from "../types";
import PositionRow from "./PositionRow";


interface Props {
  menuOption: MenuOption;
  positions: Position[];
  pipelines: Pipeline[];
  currentPrices: Object;
  decimals: Decimals
}

const PositionsPanel = (props: Props) => {

  const { menuOption, positions, currentPrices, pipelines, decimals } = props

  return (
      <StyledSegment basic className="flex-column">
        <Header size={'large'} dividing>
          <span style={{marginRight: 10}}>{menuOption.emoji}</span>
          {menuOption.text}
        </Header>
        <Table basic='very' striped>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell width={2}>Trading Bot</Table.HeaderCell>
              <Table.HeaderCell>Mode</Table.HeaderCell>
              <Table.HeaderCell>Symbol</Table.HeaderCell>
              <Table.HeaderCell>Open since</Table.HeaderCell>
              <Table.HeaderCell>Position</Table.HeaderCell>
              <Table.HeaderCell>Amount</Table.HeaderCell>
              <Table.HeaderCell>Entry Price</Table.HeaderCell>
              <Table.HeaderCell>Mark Price</Table.HeaderCell>
              <Table.HeaderCell>Leverage</Table.HeaderCell>
              <Table.HeaderCell>Net Profit</Table.HeaderCell>
              <Table.HeaderCell>Exchange</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {positions.map((position, index) => {
              return <PositionRow
                  index={index}
                  position={position}
                  pipelines={pipelines}
                  currentPrices={currentPrices}
                  decimals={decimals}
              />
            })}
          </Table.Body>
        </Table>
      </StyledSegment>
  );
};

export default PositionsPanel;