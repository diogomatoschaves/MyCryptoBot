import React from 'react';
import {Message, Table} from "semantic-ui-react";
import StyledSegment from "../styledComponents/StyledSegment";
import {Decimals, PipelinesObject, Position} from "../types";
import PositionRow from "./PositionRow";


interface Props {
  size: string
  positions: Position[];
  pipelines: PipelinesObject;
  currentPrices: Object;
  decimals: Decimals
}

const PositionsPanel = (props: Props) => {

  const { size, positions, currentPrices, pipelines, decimals } = props

  const mobile = ['mobile'].includes(size)
  const cellType = mobile ? 'div' : 'th'
  const headerStyle = mobile ? styles.header : {}

  const positionsHeader = [
    <Table.HeaderCell as={cellType} style={headerStyle} width={2}>Trading Bot</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Mode</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Symbol</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Open since</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Side</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Size</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Units</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Entry Price</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Mark Price</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Leverage</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>PnL (ROI%)</Table.HeaderCell>,
    <Table.HeaderCell as={cellType} style={headerStyle}>Exchange</Table.HeaderCell>,
  ]

  return (
      <StyledSegment padding={'40px'} basic className="flex-column">
        <Table basic='very' striped compact textAlign={'center'}>
          {!mobile && (
            <Table.Header>
              <Table.Row>
                {positionsHeader.map(entry => entry)}
              </Table.Row>
            </Table.Header>
          )}
          <Table.Body>
            {positions.map((position, index) => {
              return (
                <PositionRow
                  size={size}
                  index={index}
                  position={position}
                  pipelines={pipelines}
                  currentPrices={currentPrices}
                  decimals={decimals}
                  positionsHeader={positionsHeader}
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

const styles = {
  header: {
    fontWeight: '600'
  }
}