import styled, {css} from "styled-components";


const Wrapper: any = styled.div`
    padding: 20px;
    // height: 100%;
    width: 100%;
    overflow-y: scroll;
    ${(props: any) =>
      props.maxHeight &&
      css`
          max-height: ${props.maxHeight};
        `}
`

export default Wrapper