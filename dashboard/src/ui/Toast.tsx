import React from 'react'
import styled from 'styled-components'
import {CheckCircle2, XCircle} from 'lucide-react'

const ToastWrap = styled.div<{$visible: boolean; $success: boolean}>`
  position: fixed;
  bottom: 28px;
  left: 50%;
  z-index: 2000;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: var(--radius);
  background: var(--bg-elevated);
  border: 1px solid
    ${({$success}) => ($success ? 'rgba(46, 230, 168, 0.45)' : 'rgba(255, 84, 112, 0.45)')};
  box-shadow: var(--shadow-pop),
    0 0 32px -10px
      ${({$success}) => ($success ? 'rgba(46, 230, 168, 0.4)' : 'rgba(255, 84, 112, 0.4)')};
  color: var(--text);
  font-size: 13px;
  font-weight: 500;
  max-width: min(480px, calc(100vw - 32px));
  transform: translate(-50%, ${({$visible}) => ($visible ? '0' : '120px')});
  opacity: ${({$visible}) => ($visible ? 1 : 0)};
  transition: transform 0.35s cubic-bezier(0.2, 0.9, 0.3, 1.2), opacity 0.3s ease;
  pointer-events: none;

  svg {
    width: 17px;
    height: 17px;
    flex-shrink: 0;
    color: ${({$success}) => ($success ? 'var(--green)' : 'var(--red)')};
  }
`

interface Props {
  visible: boolean
  success: boolean
  message: React.ReactNode
}

const Toast = ({visible, success, message}: Props) => (
  <ToastWrap $visible={visible} $success={success}>
    {success ? <CheckCircle2/> : <XCircle/>}
    <span>{message}</span>
  </ToastWrap>
)

export default Toast
