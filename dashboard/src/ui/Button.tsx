import React from 'react'
import styled, {css} from 'styled-components'
import Spinner from './Spinner'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'success'
export type ButtonSize = 'sm' | 'md'

interface StyledProps {
  $variant: ButtonVariant
  $size: ButtonSize
  $fullWidth?: boolean
}

const variantStyles = {
  primary: css`
    background: var(--accent);
    color: #10150a;
    border: 1px solid transparent;
    &:hover:not(:disabled) {
      filter: brightness(1.08);
      box-shadow: 0 0 24px -6px rgba(198, 244, 50, 0.55);
    }
  `,
  secondary: css`
    background: var(--bg-elevated);
    color: var(--text);
    border: 1px solid var(--border-strong);
    &:hover:not(:disabled) {
      border-color: #3a4761;
      background: #1a2334;
    }
  `,
  ghost: css`
    background: transparent;
    color: var(--text-dim);
    border: 1px solid transparent;
    &:hover:not(:disabled) {
      color: var(--text);
      background: rgba(255, 255, 255, 0.04);
    }
  `,
  danger: css`
    background: var(--red-dim);
    color: var(--red);
    border: 1px solid rgba(255, 84, 112, 0.35);
    &:hover:not(:disabled) {
      background: rgba(255, 84, 112, 0.2);
      box-shadow: 0 0 20px -8px rgba(255, 84, 112, 0.5);
    }
  `,
  success: css`
    background: var(--green-dim);
    color: var(--green);
    border: 1px solid rgba(46, 230, 168, 0.35);
    &:hover:not(:disabled) {
      background: rgba(46, 230, 168, 0.2);
      box-shadow: 0 0 20px -8px rgba(46, 230, 168, 0.5);
    }
  `,
}

const StyledButton = styled.button<StyledProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-ui);
  font-weight: 600;
  letter-spacing: 0.02em;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  ${({$size}) =>
    $size === 'sm'
      ? css`
          font-size: 12px;
          padding: 7px 12px;
        `
      : css`
          font-size: 13px;
          padding: 10px 16px;
        `}
  ${({$variant}) => variantStyles[$variant]}
  ${({$fullWidth}) => $fullWidth && css`width: 100%;`}

  &:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  &:active:not(:disabled) {
    transform: translateY(1px);
  }
`

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  fullWidth?: boolean
  loading?: boolean
  icon?: React.ReactNode
  children?: React.ReactNode
}

const Button = ({
  variant = 'secondary',
  size = 'md',
  fullWidth,
  loading,
  icon,
  children,
  disabled,
  ...rest
}: Props) => (
  <StyledButton
    $variant={variant}
    $size={size}
    $fullWidth={fullWidth}
    disabled={disabled || loading}
    {...rest}
  >
    {loading ? <Spinner size={size === 'sm' ? 12 : 14} /> : icon}
    {children}
  </StyledButton>
)

export default Button
