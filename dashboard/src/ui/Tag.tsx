import React from 'react'
import styled from 'styled-components'
import {hexToRgba} from './utils'
import {theme} from '../theme'

const StyledTag = styled.span<{$bg: string; $color: string; $border: string; $mono?: boolean}>`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 9px;
  border-radius: 999px;
  background: ${({$bg}) => $bg};
  border: 1px solid ${({$border}) => $border};
  color: ${({$color}) => $color};
  font-family: ${({$mono}) => ($mono ? 'var(--font-mono)' : 'var(--font-ui)')};
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  white-space: nowrap;
  max-width: 100%;

  & > span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
`

interface Props {
  color?: string
  children: React.ReactNode
  mono?: boolean
  maxWidth?: string
  style?: React.CSSProperties
  title?: string
}

// Soft pill: translucent fill derived from its identity color.
const Tag = ({color = theme.textDim, children, mono = true, maxWidth, style, title}: Props) => (
  <StyledTag
    $bg={hexToRgba(color, 0.12)}
    $border={hexToRgba(color, 0.35)}
    $color={color}
    $mono={mono}
    style={{...(maxWidth ? {maxWidth} : {}), ...style}}
    title={title}
  >
    <span>{children}</span>
  </StyledTag>
)

export default Tag
