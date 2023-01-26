import React from 'react';
import {Message, Table} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {Decimals, PipelinesObject, Position} from "../types";
import PositionRow from "./PositionRow";


interface Props {
  positions: Position[];
  pipelines: PipelinesObject;
  currentPrices: Object;
  decimals: Decimals
}

const PositionsPanel = (props: Props) => {

  const { positions, currentPrices, pipelines, decimals } = props

  return (
      <StyledSegment basic className="flex-column">
        <Table basic='very' striped>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell width={2}>Trading Bot</Table.HeaderCell>
              <Table.HeaderCell>Mode</Table.HeaderCell>
              <Table.HeaderCell>Symbol</Table.HeaderCell>
              <Table.HeaderCell>Open since</Table.HeaderCell>
              <Table.HeaderCell>Side</Table.HeaderCell>
              <Table.HeaderCell>Size</Table.HeaderCell>
              <Table.HeaderCell>Units</Table.HeaderCell>
              <Table.HeaderCell>Entry Price</Table.HeaderCell>
              <Table.HeaderCell>Mark Price</Table.HeaderCell>
              <Table.HeaderCell>Leverage</Table.HeaderCell>
              <Table.HeaderCell>Net Profit</Table.HeaderCell>
              <Table.HeaderCell>Exchange</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {positions.map((position, index) => {
              return (
                <PositionRow
                  index={index}
                  position={position}
                  pipelines={pipelines}
                  currentPrices={currentPrices}
                  decimals={decimals}
                />
              )
            })}
          </Table.Body>
        </Table>
          {positions.length == 0 && (
              <Message style={{width: "100%"}}>
                <Message.Header>
                  There are no open positions.
                </Message.Header>
              </Message>
          )}
      </StyledSegment>
  );
};

export default PositionsPanel;