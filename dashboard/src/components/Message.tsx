import React from 'react'
import styled, {css} from 'styled-components'
import { StyledBox } from '../styledComponents'

interface Props {
  message: string | null
  color: string
}

const StyledMessage = styled(StyledBox)`
  &.ui.segment {
    font-size: 1.1em;
    font-weight: 600;
    margin: 3px;
    ${(props: any) =>
      props.color &&
      css`
        color: ${props.color};
      `}
  }
`

export default function Message({ message, color }: Props) {
  return <StyledMessage padded={true} color={color}>{message}</StyledMessage>
}