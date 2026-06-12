import React from 'react'
import styled from 'styled-components'

const Wrap = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 48px 24px;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  text-align: center;
  animation: fadeUp 0.35s ease both;

  svg {
    width: 28px;
    height: 28px;
    color: var(--text-faint);
  }
`

const Title = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: var(--text-dim);
`

const Hint = styled.div`
  font-size: 12px;
  color: var(--text-faint);
`

interface Props {
  icon?: React.ReactNode
  title: React.ReactNode
  hint?: React.ReactNode
  style?: React.CSSProperties
}

const EmptyState = ({icon, title, hint, style}: Props) => (
  <Wrap style={style}>
    {icon}
    <Title>{title}</Title>
    {hint && <Hint>{hint}</Hint>}
  </Wrap>
)

export default EmptyState
