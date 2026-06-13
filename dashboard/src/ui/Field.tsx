import React from 'react'
import styled from 'styled-components'

const FieldWrap = styled.div`
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: 0;
`

const Label = styled.label`
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-dim);
`

const Hint = styled.span`
  font-size: 11px;
  color: var(--text-faint);
`

interface Props {
  label?: React.ReactNode
  hint?: React.ReactNode
  children: React.ReactNode
  style?: React.CSSProperties
}

const Field = ({label, hint, children, style}: Props) => (
  <FieldWrap style={style}>
    {label && <Label>{label}</Label>}
    {children}
    {hint && <Hint>{hint}</Hint>}
  </FieldWrap>
)

export default Field
