import styled, {css} from 'styled-components'

export const Card = styled.div<{$interactive?: boolean; $padding?: string}>`
  background: var(--bg-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  padding: ${({$padding}) => $padding || '20px'};
  ${({$interactive}) =>
    $interactive &&
    css`
      cursor: pointer;
      transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
      &:hover {
        border-color: var(--border-strong);
        transform: translateY(-2px);
        box-shadow: 0 14px 36px -14px rgba(0, 0, 0, 0.7);
      }
    `}
`

export const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
`

export const CardTitle = styled.h3`
  margin: 0;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 8px;
`
