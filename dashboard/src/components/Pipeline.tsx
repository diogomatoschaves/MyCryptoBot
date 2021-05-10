import {ActivePipeline, StopPipeline} from "../types";
import {Button, Grid, Segment} from "semantic-ui-react";
import {DARK_YELLOW} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";
import styled from "styled-components";
import {stopBot} from "../apiCalls";



const PipelineDiv = styled.div`
    width: 100%;
`

interface Props extends ActivePipeline {
    stopPipeline: StopPipeline
}


function Pipeline(props: Props) {

    const { symbol, strategy, params, candleSize, exchange, stopPipeline } = props

    return (
        <PipelineDiv className="flex-row">
            <Segment style={styles.segment}>
                <Ribbon ribbon>
                    <span style={{color: DARK_YELLOW}}>{symbol}</span>
                </Ribbon>
                <Grid columns={2}>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Strategy
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {strategy}
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Parameters
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {JSON.stringify(params)}
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Candle size
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {candleSize}
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row style={styles.row}>
                        <Grid.Column floated='left' style={styles.leftColumn}>
                            Exchange
                        </Grid.Column>
                        <Grid.Column floated='right' style={styles.rightColumn} >
                            {exchange}
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
            <div style={styles.buttonDiv} className='flex-column'>
                <Button
                    onClick={() => stopPipeline({symbol, exchange})}
                    style={styles.button}
                    color={'red'}
                >
                    Stop Pipeline
                </Button>
            </div>
        </PipelineDiv>
    );
}

export default Pipeline;


const styles = {
    segment: {
        width: '80%',
        padding: '30px 30px 20px'
    },
    row: {
        paddingTop: '5px',
        paddingBottom: '5px',
    },
    leftColumn: {
        color: 'rgb(130, 130, 130)',
        fontWeight: 'bold',
        textAlign: 'left'
    },
    rightColumn: {
        textAlign: 'right',
        fontWeight: '600',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis'
    },
    button: {
        width: '80%'
    },
    buttonDiv: {
        width: '20%'
    }
}
