import {Position} from "../types";
import {Table} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";
import React from "react";
import {timeFormatter} from "../utils/helpers";


interface Props {
  index: number
  position: Position;
}

function PositionRow(props: Props) {

  const { position, index } = props

  const negative = position.position === -1
  const positive = position.position === 1
  const positionSide = positive ? "LONG" : negative ? "SHORT" : "NEUTRAL"
  const color = negative ? RED : positive ? GREEN : DARK_YELLOW

  const age = timeFormatter(position.openTime)

  const decimalPlaces = 3

  return (
      <Table.Row active={index % 2 == 0} key={index} >
        <Table.Cell style={{fontWeight: 600, color: DARK_YELLOW}}>{position.symbol}</Table.Cell>
        <Table.Cell>{position.exchange}</Table.Cell>
        <Table.Cell>{position.open ? "Open": " Closed"}</Table.Cell>
        <Table.Cell style={{color, fontWeight: '600'}}>{positionSide}</Table.Cell>
        <Table.Cell>{Number(position.amount).toFixed(decimalPlaces)}</Table.Cell>
        <Table.Cell>{Number(position.price).toFixed(decimalPlaces)}</Table.Cell>
        <Table.Cell>{age}</Table.Cell>
        <Table.Cell>{position.paperTrading ? "Yes" : "No"}</Table.Cell>
      </Table.Row>
  );
}

export default PositionRow;


const styles = {
  defaultCell: {
    color: 'rgb(70, 70, 70)',
    fontWeight: '500',
  },
  quantityCell: {
    // color: TEAL,
    fontWeight: '500',
  }
}
