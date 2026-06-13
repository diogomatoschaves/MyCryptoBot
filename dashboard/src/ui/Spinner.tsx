import styled from 'styled-components'

const Spinner = styled.span<{size?: number; color?: string}>`
  display: inline-block;
  width: ${({size}) => size || 16}px;
  height: ${({size}) => size || 16}px;
  border-radius: 50%;
  border: 2px solid ${({color}) => color || 'currentColor'};
  border-top-color: transparent;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
`

export default Spinner
