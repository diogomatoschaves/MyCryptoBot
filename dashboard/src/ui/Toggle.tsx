import styled from 'styled-components'

const ToggleWrap = styled.label<{$disabled?: boolean}>`
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: ${({$disabled}) => ($disabled ? 'not-allowed' : 'pointer')};
  opacity: ${({$disabled}) => ($disabled ? 0.5 : 1)};
  user-select: none;

  input {
    display: none;
  }
`

const Track = styled.span<{$checked: boolean}>`
  position: relative;
  width: 38px;
  height: 21px;
  border-radius: 999px;
  flex-shrink: 0;
  background: ${({$checked}) => ($checked ? 'var(--accent)' : 'var(--bg-elevated)')};
  border: 1px solid ${({$checked}) => ($checked ? 'transparent' : 'var(--border-strong)')};
  transition: background 0.18s ease;

  &::after {
    content: '';
    position: absolute;
    top: 2px;
    left: ${({$checked}) => ($checked ? '19px' : '2px')};
    width: 15px;
    height: 15px;
    border-radius: 50%;
    background: ${({$checked}) => ($checked ? '#10150a' : 'var(--text-dim)')};
    transition: left 0.18s ease, background 0.18s ease;
  }
`

const ToggleLabel = styled.span`
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
`

interface Props {
  checked: boolean
  onChange: () => void
  label?: React.ReactNode
  disabled?: boolean
}

const Toggle = ({checked, onChange, label, disabled}: Props) => (
  <ToggleWrap $disabled={disabled}>
    <input
      type="checkbox"
      checked={checked}
      disabled={disabled}
      onChange={() => !disabled && onChange()}
    />
    <Track $checked={checked}/>
    {label && <ToggleLabel>{label}</ToggleLabel>}
  </ToggleWrap>
)

export default Toggle
