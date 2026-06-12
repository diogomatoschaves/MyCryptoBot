import {Layers} from 'lucide-react'
import {Decimals, PipelinesObject, Position} from "../types";
import PositionRow from "./PositionRow";
import {EmptyState, Table, TableScroll} from "../ui";


const POSITIONS_HEADER = [
  'Trading Bot',
  'Mode',
  'Symbol',
  'Open since',
  'Side',
  'Size',
  'Units',
  'Entry Price',
  'Mark Price',
  'Leverage',
  'PnL (ROI%)',
  'Exchange',
]


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

  if (positions.length === 0) {
    return (
      <EmptyState
        icon={<Layers/>}
        title="There are no open positions"
        hint="Positions opened by your trading bots will show up here."
      />
    )
  }

  const rows = positions.map((position, index) => (
    <PositionRow
      key={`${position.pipelineId}-${position.symbol}-${index}`}
      size={size}
      index={index}
      position={position}
      pipelines={pipelines}
      currentPrices={currentPrices}
      decimals={decimals}
      positionsHeader={POSITIONS_HEADER}
    />
  ))

  if (mobile) {
    return <div style={{width: '100%', animation: 'fadeUp 0.35s ease both'}}>{rows}</div>
  }

  return (
    <TableScroll style={{animation: 'fadeUp 0.35s ease both'}}>
      <Table>
        <thead>
          <tr>
            {POSITIONS_HEADER.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </Table>
    </TableScroll>
  );
};

export default PositionsPanel;
