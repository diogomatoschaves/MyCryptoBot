import styled, { css } from 'styled-components'

const Box: any = styled.div`
  width: ${(props: any) => (props.width ? props.width : '100%')};
  height: ${(props: any) => props.height && props.height};
  padding: ${(props: any) => props.padding && props.padding};
  display: flex;
  flex-direction: ${(props: any) => (props.direction ? props.direction : 'column')};
  justify-content: ${(props: any) => props.justify && props.justify};
  align-items: ${(props: any) => (props.align ? props.align : 'center')};
  ${(props: any) =>
    props.position &&
    css`
      position: ${props.position};
    `}
  ${(props: any) =>
    props.top &&
    css`
      top: ${props.top};
    `}
  ${(props: any) =>
    props.bottom &&
    css`
      bottom: ${props.bottom};
    `}
  ${(props: any) =>
    props.left &&
    css`
      left: ${props.left};
    `}
  ${(props: any) =>
    props.right &&
    css`
      right: ${props.right};
    `}
  ${(props: any) =>
    props.zindex &&
    css`
      z-index: ${props.zindex};
    `}
  ${(props: any) =>
    props.cursor &&
    css`
      cursor: ${props.cursor};
    `}
  ${(props: any) =>
    props.borderradius &&
    css`
      border-radius: ${props.borderradius};
    `}
  ${(props: any) =>
    props.opacity &&
    css`
      opacity: ${props.opacity};
    `}
  
` as any

export default Box