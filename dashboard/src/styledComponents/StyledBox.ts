import { Segment } from 'semantic-ui-react'
import styled, { css } from 'styled-components'

const StyledBox: any = styled(Segment as any)`
  ${(props: any) =>
    props.width &&
    css`
      width: ${props.width};
    `}
  ${(props: any) =>
    props.height &&
    css`
      height: ${props.height};
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
  color: ${(props: any) => (props.overridecolor ? props.overridecolor : 'black')};
  ${(props: any) =>
    props.fontSize &&
    css`
      font-size: ${props.fontSize};
    `}
  ${(props: any) =>
    props.borderradius &&
    css`
      border-radius: ${props.borderradius};
    `}
  &.ui.segment {
    ${(props: any) =>
    props.position &&
    css`
        position: ${props.position};
      `};
    ${(props: any) =>
    props.padding &&
    css`
        padding: ${props.padding};
      `};
    ${(props: any) =>
    props.margin &&
    css`
        padding: ${props.margin};
      `};
    border: none;
    border-radius: 10px;
    background: ${props =>
    props.background ? props.background : 'rgba(255, 255, 255, 0.92)'};
    box-shadow: ${props =>
    !props.noBoxShadow ? '10px 10px 16px -9px rgba(77,77,77,0.5)' : 'none'};
  }
  font-family: "BasisGrotesque Medium", Lato,'Helvetica Neue',Arial,Helvetica,sans-serif;
` as any

export default StyledBox