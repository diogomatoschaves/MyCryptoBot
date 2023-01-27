import styled from "styled-components";
import {Label} from "semantic-ui-react";

const Ribbon = styled(Label)`
  font-size: 1.1em !important;
  font-weight: 800 !important;
  white-space: nowrap;
  border-top-left-radius: 5px !important;
  text-align: center;
  position: absolute !important;
  top: -17px;
  left: -19px !important;
  align-self: flex-start;
  
  & > * {
    margin-left: -10px;
  } 
`

export default Ribbon