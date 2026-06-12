import styled from 'styled-components'

export const TableScroll = styled.div<{$maxHeight?: string}>`
  width: 100%;
  overflow: auto;
  max-height: ${({$maxHeight}) => $maxHeight || 'none'};
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-raised);
  box-shadow: var(--shadow-card);
`

export const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;

  thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: var(--bg-elevated);
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dim);
    text-align: left;
    padding: 12px 14px;
    border-bottom: 1px solid var(--border-strong);
    white-space: nowrap;
  }

  tbody td {
    padding: 12px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    white-space: nowrap;
    vertical-align: middle;
  }

  tbody tr {
    transition: background 0.12s ease;
  }

  tbody tr:hover {
    background: rgba(255, 255, 255, 0.025);
  }

  tbody tr:last-child td {
    border-bottom: none;
  }
`

export const Num = styled.span<{$color?: string}>`
  font-family: var(--font-mono);
  font-weight: 500;
  color: ${({$color}) => $color || 'var(--text)'};
`

// Mobile fallback: each row rendered as a stacked card of label/value pairs.
export const MobileRowCard = styled.div`
  background: var(--bg-raised);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
`

export const MobileRowLine = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;

  & > span:first-child {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-faint);
    flex-shrink: 0;
  }
`
