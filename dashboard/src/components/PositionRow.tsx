import {Position} from "../types";
import {Label, Table} from "semantic-ui-react";
import {DARK_YELLOW, GREEN, RED} from "../utils/constants";
import React from "react";
import {getPnl, timeFormatter} from "../utils/helpers";


interface Props {
  index: number
  position: Position;
  currentPrices: Object
}

function PositionRow(props: Props) {

  const { position, index, currentPrices } = props

  const negative = position.position === -1
  const positive = position.position === 1
  const positionSide = positive ? "LONG" : negative ? "SHORT" : "NEUTRAL"
  const color = negative ? RED : positive ? GREEN : DARK_YELLOW

  const age = timeFormatter(position.openTime)

  const decimalPlaces = 3

  // @ts-ignore
  const pnl = currentPrices[position.symbol] ? getPnl(position.price, currentPrices[position.symbol], position.position)
      : 0

  const pnlColor = pnl > 0 ? GREEN : RED

  return (
      <Table.Row key={index}>
        <Table.Cell style={styles.defaultCell}>
          <Label ribbon>{position.paperTrading ? "Demo" : "Live"}</Label>
        </Table.Cell>
        <Table.Cell style={{...styles.defaultCell, fontWeight: 600}}>
          <Label color={'pink'}>{position.pipelineName}</Label>
        </Table.Cell>
        <Table.Cell style={{fontWeight: 600, color: DARK_YELLOW}}>{position.symbol}</Table.Cell>
        <Table.Cell style={styles.defaultCell}>{age}</Table.Cell>
        <Table.Cell style={{color, fontWeight: '600'}}>{positionSide}</Table.Cell>
        <Table.Cell style={styles.defaultCell}>{Number(position.amount).toFixed(decimalPlaces)}</Table.Cell>
        <Table.Cell style={styles.defaultCell}>{Number(position.price).toFixed(decimalPlaces)}</Table.Cell>
        <Table.Cell style={{...styles.defaultCell, ...styles.quantityCell, color: pnlColor}}>
          {pnl && `${pnl}%`}
        </Table.Cell>
        <Table.Cell style={styles.defaultCell}>{position.exchange}</Table.Cell>
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
