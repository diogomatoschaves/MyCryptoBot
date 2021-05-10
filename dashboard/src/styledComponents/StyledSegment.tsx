import styled from "styled-components";
import {Segment} from "semantic-ui-react";


const StyledSegment = styled(Segment)`
    width: 100%;
    height: 100%;
    justify-content: flex-start;
    align-items: center;
    
    &.ui.segment {
        padding: 25px;
        padding-top: 0;
    }
`

export default StyledSegment
