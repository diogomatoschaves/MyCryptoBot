import React, {useEffect} from 'react'
import {createPortal} from 'react-dom'
import styled from 'styled-components'
import {X} from 'lucide-react'

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: var(--bg-overlay);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 7vh 16px 16px;
  overflow-y: auto;
  animation: fadeIn 0.15s ease;
`

const Panel = styled.div<{$width?: string}>`
  width: 100%;
  max-width: ${({$width}) => $width || '560px'};
  background: var(--bg-raised);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  box-shadow: var(--shadow-pop);
  animation: scaleIn 0.18s ease;
  margin-bottom: 40px;
`

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 22px;
  border-bottom: 1px solid var(--border);
`

const Title = styled.h2`
  margin: 0;
  font-family: var(--font-ui);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.01em;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 10px;
`

const CloseButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text-faint);
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    color: var(--text);
  }

  svg {
    width: 16px;
    height: 16px;
  }
`

const Body = styled.div`
  padding: 22px;
`

const Footer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 22px;
  border-top: 1px solid var(--border);
`

interface Props {
  open: boolean
  onClose: () => void
  title?: React.ReactNode
  footer?: React.ReactNode
  width?: string
  children: React.ReactNode
}

const Modal = ({open, onClose, title, footer, width, children}: Props) => {
  useEffect(() => {
    if (!open) return
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKey)
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleKey)
      document.body.style.overflow = previousOverflow
    }
  }, [open, onClose])

  if (!open) return null

  return createPortal(
    <Overlay
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
      onClick={(event) => event.stopPropagation()}
    >
      <Panel $width={width}>
        {title !== undefined && (
          <Header>
            <Title>{title}</Title>
            <CloseButton onClick={onClose} aria-label="Close">
              <X/>
            </CloseButton>
          </Header>
        )}
        <Body>{children}</Body>
        {footer && <Footer>{footer}</Footer>}
      </Panel>
    </Overlay>,
    document.body
  )
}

export default Modal
