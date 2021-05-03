import {ActivePipeline} from "../types";
import {Grid, Segment} from "semantic-ui-react";
import {DARK_YELLOW} from "../utils/constants";
import Ribbon from "../styledComponents/Ribbon";


interface Props {
    pipeline: ActivePipeline
}


function Pipeline(props: Props) {

    const { pipeline } = props

    return (
        <Segment style={styles.segment}>
            <Ribbon ribbon>
                <span style={{color: DARK_YELLOW}}>{pipeline.symbol}</span>
            </Ribbon>
            <Grid columns={2}>
                <Grid.Row style={styles.row}>
                    <Grid.Column floated='left' style={styles.leftColumn}>
                        Strategy
                    </Grid.Column>
                    <Grid.Column floated='right' style={styles.rightColumn} >
                        {pipeline.strategy}
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row style={styles.row}>
                    <Grid.Column floated='left' style={styles.leftColumn}>
                        Parameters
                    </Grid.Column>
                    <Grid.Column floated='right' style={styles.rightColumn} >
                        {JSON.stringify(pipeline.params)}
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row style={styles.row}>
                    <Grid.Column floated='left' style={styles.leftColumn}>
                        Candle size
                    </Grid.Column>
                    <Grid.Column floated='right' style={styles.rightColumn} >
                        {pipeline.candleSize}
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row style={styles.row}>
                    <Grid.Column floated='left' style={styles.leftColumn}>
                        Exchange
                    </Grid.Column>
                    <Grid.Column floated='right' style={styles.rightColumn} >
                        {pipeline.exchange}
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </Segment>
    );
}

export default Pipeline;


const styles = {
    segment: {
        width: '100%',
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
    }
}
