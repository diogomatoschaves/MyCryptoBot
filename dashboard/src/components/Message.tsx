import React from 'react'
import styled, {css} from 'styled-components'
import { StyledBox } from '../styledComponents'
import {Message} from "semantic-ui-react";

interface Props {
  message: string | null
  color?: string,
  success: boolean
}

const StyledMessage = styled(Message)`
  &.ui.message {
    
  }
`

export default function UserMessage({ success, message, color }: Props) {
  return <StyledMessage
      success={success}
      negative={!success}
      padded={true}
      color={color}
  >
    <StyledMessage.Header>
      {message}
    </StyledMessage.Header>
  </StyledMessage>
}