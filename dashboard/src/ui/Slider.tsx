import styled from 'styled-components'

const SliderWrap = styled.div<{$disabled?: boolean}>`
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  opacity: ${({$disabled}) => ($disabled ? 0.5 : 1)};
`

const Range = styled.input<{$pct: number}>`
  -webkit-appearance: none;
  appearance: none;
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(
    to right,
    var(--accent) 0%,
    var(--accent) ${({$pct}) => $pct}%,
    var(--bg-elevated) ${({$pct}) => $pct}%,
    var(--bg-elevated) 100%
  );
  outline: none;
  cursor: ${({disabled}) => (disabled ? 'not-allowed' : 'pointer')};

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--accent);
    border: 3px solid #10150a;
    box-shadow: 0 0 0 1px var(--accent);
    transition: transform 0.1s ease;
  }

  &::-webkit-slider-thumb:hover {
    transform: scale(1.15);
  }

  &::-moz-range-thumb {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--accent);
    border: 2px solid #10150a;
    box-shadow: 0 0 0 1px var(--accent);
  }
`

const Value = styled.span`
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  min-width: 38px;
  text-align: right;
`

interface Props {
  min: number
  max: number
  value: number
  onChange: (value: number) => void
  disabled?: boolean
  formatValue?: (value: number) => string
}

const Slider = ({min, max, value, onChange, disabled, formatValue}: Props) => {
  const pct = ((value - min) / (max - min)) * 100
  return (
    <SliderWrap $disabled={disabled}>
      <Range
        type="range"
        min={min}
        max={max}
        value={value}
        disabled={disabled}
        $pct={pct}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <Value>{formatValue ? formatValue(value) : value}</Value>
    </SliderWrap>
  )
}

export default Slider
