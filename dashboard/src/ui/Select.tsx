import React, {useEffect, useMemo, useRef, useState} from 'react'
import styled from 'styled-components'
import {Check, ChevronDown, X} from 'lucide-react'
import {hexToRgba} from './utils'

export interface SelectOption {
  value: number | string
  label: string
  color?: string
}

const Wrap = styled.div<{$disabled?: boolean}>`
  position: relative;
  width: 100%;
  opacity: ${({$disabled}) => ($disabled ? 0.5 : 1)};
`

const Trigger = styled.div<{$open: boolean; $disabled?: boolean}>`
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
  min-height: 38px;
  padding: 5px 34px 5px 10px;
  background: var(--bg-input);
  border: 1px solid ${({$open}) => ($open ? 'var(--accent)' : 'var(--border-strong)')};
  border-radius: var(--radius-sm);
  cursor: ${({$disabled}) => ($disabled ? 'not-allowed' : 'pointer')};
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  box-shadow: ${({$open}) => ($open ? '0 0 0 3px rgba(198, 244, 50, 0.12)' : 'none')};
`

const Placeholder = styled.span`
  color: var(--text-faint);
  font-size: 13px;
  padding: 4px 2px;
`

const SingleValue = styled.span`
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text);
  font-size: 13px;
  padding: 4px 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

const Chip = styled.span<{$color?: string}>`
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  background: ${({$color}) => ($color ? hexToRgba($color, 0.14) : 'var(--bg-elevated)')};
  border: 1px solid ${({$color}) => ($color ? hexToRgba($color, 0.4) : 'var(--border-strong)')};
  color: ${({$color}) => $color || 'var(--text)'};

  svg {
    width: 12px;
    height: 12px;
    cursor: pointer;
    opacity: 0.7;

    &:hover {
      opacity: 1;
    }
  }
`

const SearchInput = styled.input`
  flex: 1;
  min-width: 60px;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 13px;
  padding: 4px 2px;

  &::placeholder {
    color: var(--text-faint);
  }
`

const Chevron = styled.span<{$open: boolean}>`
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%) rotate(${({$open}) => ($open ? '180deg' : '0deg')});
  transition: transform 0.18s ease;
  color: var(--text-faint);
  display: flex;
  pointer-events: none;

  svg {
    width: 16px;
    height: 16px;
  }
`

const Menu = styled.div`
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 50;
  background: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-pop);
  max-height: 240px;
  overflow-y: auto;
  padding: 4px;
  animation: scaleIn 0.12s ease;
`

const Option = styled.div<{$selected?: boolean; $highlighted?: boolean}>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  color: ${({$selected}) => ($selected ? 'var(--accent)' : 'var(--text)')};
  background: ${({$highlighted}) => ($highlighted ? 'rgba(255, 255, 255, 0.05)' : 'transparent')};

  svg {
    width: 14px;
    height: 14px;
    flex-shrink: 0;
  }
`

const Dot = styled.span<{$color: string}>`
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
  background: ${({$color}) => $color};
  box-shadow: 0 0 8px ${({$color}) => hexToRgba($color, 0.6)};
`

const NoResults = styled.div`
  padding: 12px;
  text-align: center;
  font-size: 12px;
  color: var(--text-faint);
`

interface Props {
  options: SelectOption[]
  value?: number | string | Array<number | string> | null
  onChange: (value: any) => void
  multi?: boolean
  searchable?: boolean
  placeholder?: string
  disabled?: boolean
}

const Select = ({options, value, onChange, multi, searchable, placeholder, disabled}: Props) => {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [highlighted, setHighlighted] = useState(0)
  const wrapRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  const selectedValues: Array<number | string> = multi
    ? ((value as Array<number | string>) || [])
    : value !== null && value !== undefined && value !== ''
      ? [value as number | string]
      : []

  const filtered = useMemo(() => {
    if (!search) return options
    const term = search.toLowerCase()
    return options.filter((option) => option.label.toLowerCase().includes(term))
  }, [options, search])

  useEffect(() => {
    const handleOutside = (event: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(event.target as Node)) {
        setOpen(false)
        setSearch('')
      }
    }
    document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [])

  useEffect(() => {
    if (open && searchable) searchRef.current?.focus()
    if (!open) setHighlighted(0)
  }, [open, searchable])

  const selectOption = (option: SelectOption) => {
    if (multi) {
      const exists = selectedValues.includes(option.value)
      onChange(
        exists
          ? selectedValues.filter((v) => v !== option.value)
          : [...selectedValues, option.value]
      )
      setSearch('')
    } else {
      onChange(option.value)
      setOpen(false)
      setSearch('')
    }
  }

  const removeValue = (val: number | string, event: React.MouseEvent) => {
    event.preventDefault()
    event.stopPropagation()
    onChange(selectedValues.filter((v) => v !== val))
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      setOpen(false)
      setSearch('')
    } else if (event.key === 'ArrowDown') {
      event.preventDefault()
      setHighlighted((h) => Math.min(h + 1, filtered.length - 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setHighlighted((h) => Math.max(h - 1, 0))
    } else if (event.key === 'Enter') {
      event.preventDefault()
      if (filtered[highlighted]) selectOption(filtered[highlighted])
    }
  }

  const optionByValue = (val: number | string) => options.find((o) => o.value === val)
  const singleSelected = !multi && selectedValues.length > 0 ? optionByValue(selectedValues[0]) : null

  return (
    <Wrap ref={wrapRef} $disabled={disabled} onKeyDown={handleKeyDown}>
      <Trigger
        $open={open}
        $disabled={disabled}
        onClick={(event) => {
          event.preventDefault()
          event.stopPropagation()
          if (!disabled) setOpen(!open)
        }}
      >
        {multi &&
          selectedValues.map((val) => {
            const option = optionByValue(val)
            if (!option) return null
            return (
              <Chip key={String(val)} $color={option.color}>
                {option.label}
                <X onClick={(event) => removeValue(val, event)}/>
              </Chip>
            )
          })}
        {!multi && singleSelected && !((open && searchable)) && (
          <SingleValue>
            {singleSelected.color && <Dot $color={singleSelected.color}/>}
            {singleSelected.label}
          </SingleValue>
        )}
        {open && searchable ? (
          <SearchInput
            ref={searchRef}
            value={search}
            placeholder={!multi && singleSelected ? singleSelected.label : placeholder}
            onChange={(event) => {
              setSearch(event.target.value)
              setHighlighted(0)
            }}
            onClick={(event) => event.stopPropagation()}
          />
        ) : (
          selectedValues.length === 0 && <Placeholder>{placeholder}</Placeholder>
        )}
        <Chevron $open={open}>
          <ChevronDown/>
        </Chevron>
      </Trigger>
      {open && (
        <Menu>
          {filtered.length === 0 && <NoResults>No matches</NoResults>}
          {filtered.map((option, index) => {
            const selected = selectedValues.includes(option.value)
            return (
              <Option
                key={String(option.value)}
                $selected={selected}
                $highlighted={index === highlighted}
                onMouseEnter={() => setHighlighted(index)}
                onClick={(event) => {
                  event.preventDefault()
                  event.stopPropagation()
                  selectOption(option)
                }}
              >
                <span style={{display: 'flex', alignItems: 'center', gap: 8, minWidth: 0}}>
                  {option.color && <Dot $color={option.color}/>}
                  <span style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>
                    {option.label}
                  </span>
                </span>
                {selected && <Check/>}
              </Option>
            )
          })}
        </Menu>
      )}
    </Wrap>
  )
}

export default Select
