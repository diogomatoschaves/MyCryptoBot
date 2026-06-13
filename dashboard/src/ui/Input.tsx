import React from 'react'
import styled from 'styled-components'

const Wrap = styled.div<{$disabled?: boolean}>`
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-input);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  padding: 0 12px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  opacity: ${({$disabled}) => ($disabled ? 0.5 : 1)};

  &:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(198, 244, 50, 0.12);
  }

  input {
    flex: 1;
    min-width: 0;
    background: transparent;
    border: none;
    outline: none;
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 13px;
    padding: 10px 0;

    &::placeholder {
      color: var(--text-faint);
      font-family: var(--font-ui);
    }
  }
`

const Suffix = styled.span`
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-faint);
  letter-spacing: 0.08em;
  white-space: nowrap;
`

interface Props extends React.InputHTMLAttributes<HTMLInputElement> {
  suffix?: React.ReactNode
}

const TextInput = ({suffix, disabled, style, ...rest}: Props) => (
  <Wrap $disabled={disabled} style={style}>
    <input disabled={disabled} {...rest} />
    {suffix && <Suffix>{suffix}</Suffix>}
  </Wrap>
)

export default TextInput
