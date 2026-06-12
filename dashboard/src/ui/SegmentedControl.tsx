import styled from 'styled-components'

const Group = styled.div`
  display: inline-flex;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 3px;
  gap: 2px;
`

const Segment = styled.button<{$active: boolean}>`
  border: none;
  border-radius: 999px;
  padding: 5px 14px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s ease;
  background: ${({$active}) => ($active ? 'var(--accent-dim)' : 'transparent')};
  color: ${({$active}) => ($active ? 'var(--accent)' : 'var(--text-faint)')};

  &:hover {
    color: ${({$active}) => ($active ? 'var(--accent)' : 'var(--text-dim)')};
  }
`

export interface SegmentOption {
  value: string
  label: string
}

interface Props {
  options: SegmentOption[]
  isActive: (value: string) => boolean
  onToggle: (value: string) => void
  disabled?: boolean
  style?: React.CSSProperties
}

// A pill group where each segment can be toggled independently (used for
// filters) or treated as a radio by the caller via isActive/onToggle.
const SegmentedControl = ({options, isActive, onToggle, disabled, style}: Props) => (
  <Group style={style}>
    {options.map((option) => (
      <Segment
        key={option.value}
        type="button"
        disabled={disabled}
        $active={isActive(option.value)}
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          onToggle(option.value)
        }}
      >
        {option.label}
      </Segment>
    ))}
  </Group>
)

export default SegmentedControl
