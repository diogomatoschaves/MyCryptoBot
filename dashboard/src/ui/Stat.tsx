import React from 'react'
import styled from 'styled-components'

const StatWrap = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
`

const StatLabel = styled.span`
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-faint);
  white-space: nowrap;
`

const StatValue = styled.span<{$color?: string; $size?: 'sm' | 'md' | 'lg'}>`
  font-family: var(--font-mono);
  font-size: ${({$size}) => ($size === 'lg' ? '22px' : $size === 'sm' ? '13px' : '16px')};
  font-weight: 600;
  color: ${({$color}) => $color || 'var(--text)'};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

interface Props {
  label: string
  value: React.ReactNode
  color?: string
  size?: 'sm' | 'md' | 'lg'
  sub?: React.ReactNode
}

const Stat = ({label, value, color, size, sub}: Props) => (
  <StatWrap>
    <StatLabel>{label}</StatLabel>
    <StatValue $color={color} $size={size}>
      {value}
    </StatValue>
    {sub}
  </StatWrap>
)

export default Stat
