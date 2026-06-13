import React from 'react'
import styled from 'styled-components'
import {AlertCircle, CheckCircle2} from 'lucide-react'

const Wrap = styled.div<{$success: boolean}>`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  background: ${({$success}) => ($success ? 'var(--green-dim)' : 'var(--red-dim)')};
  border: 1px solid
    ${({$success}) => ($success ? 'rgba(46, 230, 168, 0.35)' : 'rgba(255, 84, 112, 0.35)')};
  color: ${({$success}) => ($success ? 'var(--green)' : 'var(--red)')};
  animation: fadeIn 0.2s ease;

  svg {
    width: 14px;
    height: 14px;
    flex-shrink: 0;
  }
`

interface Props {
  success: boolean
  children: React.ReactNode
}

const InlineMessage = ({success, children}: Props) => (
  <Wrap $success={success}>
    {success ? <CheckCircle2/> : <AlertCircle/>}
    <span>{children}</span>
  </Wrap>
)

export default InlineMessage
